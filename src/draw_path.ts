// Use a unique type name to avoid conflicts with edit_board.ts
type PathDot = { row: number, col: number, color: string };
type PathPoint = { row: number, col: number, color: string, route: 0 | 1 };

// Access globals via (window as any)
const rows = (window as any).DRAW_BOARD_ROWS as number;
const cols = (window as any).DRAW_BOARD_COLS as number;
const dots: PathDot[] = (window as any).DRAW_DOTS || [];
let path: PathPoint[] = (window as any).DRAW_PATH || [];

window.addEventListener('DOMContentLoaded', () => {
    const gridContainer = document.getElementById('grid-container') as HTMLElement;
    const pathJsonInput = document.getElementById('path-json') as HTMLInputElement;
    const form = document.getElementById('path-form') as HTMLFormElement;

    // Add color picker for path drawing
    let colorPicker = document.getElementById('path-color') as HTMLSelectElement | null;
    if (!colorPicker) {
        colorPicker = document.createElement('select');
        colorPicker.id = 'path-color';
        [
            {value: "#e41a1c", label: "Czerwony"},
            {value: "#377eb8", label: "Niebieski"},
            {value: "#4daf4a", label: "Zielony"},
            {value: "#984ea3", label: "Fioletowy"},
            {value: "#ff7f00", label: "Pomarańczowy"},
            {value: "#a65628", label: "Brązowy"},
            {value: "#ffd700", label: "Żółty"},
            {value: "#00ced1", label: "Turkusowy"},
            {value: "#ff69b4", label: "Różowy"},
            {value: "#228b22", label: "Ciemnozielony"},
            {value: "#8b4513", label: "SaddleBrown"},
            {value: "#4682b4", label: "Stalowy niebieski"},
            {value: "#b22222", label: "Ceglasty"},
            {value: "#00ff7f", label: "Jasnozielony"},
            {value: "#ff1493", label: "Deep Pink"},
            {value: "#ffa500", label: "Pomarańczowy 2"},
            {value: "#800080", label: "Purpurowy"},
            {value: "#00bfff", label: "Niebieski jasny"},
            {value: "#c71585", label: "Medium Violet Red"},
            {value: "#f5a623", label: "Żółtopomarańczowy"},
        ].forEach(opt => {
            const o = document.createElement('option');
            o.value = opt.value;
            o.textContent = opt.label;
            o.style.color = opt.value;
            colorPicker!.appendChild(o);
        });
        form.insertBefore(colorPicker, form.querySelector('button[type="submit"]'));
    }

    let currentColor: string = colorPicker.value;

    // Add this line at the top of DOMContentLoaded handler
    const finishedColors = new Set<string>();

    function isAdjacentToPathOrDot(row: number, col: number, color: string): boolean {
        const neighbors = [
            {row: row-1, col},
            {row: row+1, col},
            {row, col: col-1},
            {row, col: col+1}
        ];
        // Check for dots
        for (const n of neighbors) {
            if (dots.some(dot => dot.row === n.row && dot.col === n.col && dot.color === color)) {
                return true;
            }
        }
        // Check for path points
        for (const n of neighbors) {
            if (path.some(p => p.row === n.row && p.col === n.col && p.color === color)) {
                return true;
            }
        }
        // Allow first point if it's on a dot of this color
        if (
            path.filter(p => p.color === color).length === 0 &&
            dots.some(dot => dot.row === row && dot.col === col && dot.color === color)
        ) {
            return true;
        }
        return false;
    }

    function renderGrid() {
        gridContainer.innerHTML = '';
        const table = document.createElement('table');
        table.style.borderCollapse = 'collapse';
        table.style.marginTop = '1em';
        for (let r = 0; r < rows; r++) {
            const tr = document.createElement('tr');
            for (let c = 0; c < cols; c++) {
                const td = document.createElement('td');
                td.dataset.row = r.toString();
                td.dataset.col = c.toString();
                td.style.width = '40px';
                td.style.height = '40px';
                td.style.border = '1px solid #aaa';
                td.style.textAlign = 'center';
                td.style.verticalAlign = 'middle';
                td.style.cursor = 'pointer';

                // Draw dot if present
                const dot = dots.find(dot => dot.row === r && dot.col === c);
                if (dot) {
                    const circle = document.createElement('div');
                    circle.style.width = '24px';
                    circle.style.height = '24px';
                    circle.style.margin = 'auto';
                    circle.style.borderRadius = '50%';
                    circle.style.background = dot.color;
                    td.appendChild(circle);
                }

                // Draw all path points (show all colors)
                const pathPoint = path.find(p => p.row === r && p.col === c);
                if (pathPoint) {
                    td.style.background = pathPoint.color;
                }
                tr.appendChild(td);
            }
            table.appendChild(tr);
        }
        gridContainer.appendChild(table);
    }

    // Helper: Get the two dots for a color
    function getDotsForColor(color: string): [PathDot, PathDot] | null {
        const colorDots = dots.filter(dot => dot.color === color);
        if (colorDots.length === 2) return [colorDots[0], colorDots[1]];
        return null;
    }

    // Helper: Get the two paths for a color, each starting from one dot
    function getPathsForColor(color: string): [PathPoint[], PathPoint[]] | null {
        // Now, just filter by route
        const path0 = path.filter(p => p.color === color && p.route === 0);
        const path1 = path.filter(p => p.color === color && p.route === 1);
        return [path0, path1];
    }

    // Helper: Is (row,col) adjacent to a given point
    function isAdjacent(a: {row:number,col:number}, b: {row:number,col:number}) {
        return Math.abs(a.row-b.row)+Math.abs(a.col-b.col) === 1;
    }

    // Helper: Can add a point to a path (adjacent to last point)
    function canAddToPath(pathArr: PathPoint[], row: number, col: number, startDot: PathDot): boolean {
        if (pathArr.length === 0) {
            // First point: must be adjacent to startDot
            return isAdjacent({row, col}, startDot);
        } else {
            // Must be adjacent to last point in path
            const last = pathArr[pathArr.length-1];
            return isAdjacent({row, col}, last);
        }
    }

    // Returns 0 or 1 for the route, or -1 if not allowed
    function canAddPathPoint(row: number, col: number, color: string): 0 | 1 | -1 {
        // Disallow adding on top of any dot
        if (dots.some(dot => dot.row === row && dot.col === col)) return -1;
        if (finishedColors.has(color)) return -1;
        if (path.some(p => p.row === row && p.col === col && p.color === color)) return -1;

        const colorDots = getDotsForColor(color);
        if (!colorDots) return -1;
        const [dot0, dot1] = colorDots;
        const [path0, path1] = getPathsForColor(color)!;

        let canAdd0 = false, canAdd1 = false;
        if (path0.length === 0) {
            canAdd0 = isAdjacent({row, col}, dot0);
        } else {
            canAdd0 = isAdjacent({row, col}, path0[path0.length-1]);
        }

        if (path1.length === 0) {
            canAdd1 = isAdjacent({row, col}, dot1);
        } else {
            canAdd1 = isAdjacent({row, col}, path1[path1.length-1]);
        }

        if (!canAdd0 && !canAdd1) return -1;
        if (canAdd0 && canAdd1) return 0; // Arbitrarily pick 0 if both allowed

        if (canAdd0 && !canAdd1) {
            for (const p of path1) {
                if (isAdjacent({row, col}, p)) return -1;
            }
            if (isAdjacent({row, col}, dot1)) return -1;
            return 0;
        }
        if (canAdd1 && !canAdd0) {
            for (const p of path0) {
                if (isAdjacent({row, col}, p)) return -1;
            }
            if (isAdjacent({row, col}, dot0)) return -1;
            return 1;
        }
        return -1;
    }

    function handleCellClick(e: MouseEvent) {
        const target = e.target as HTMLElement;
        const td = target.closest('td');
        if (!td) return;
        const row = parseInt(td.dataset.row!, 10);
        const col = parseInt(td.dataset.col!, 10);

        const color = currentColor;
        const colorDots = getDotsForColor(color);
        if (!colorDots) return;
        const [dot0, dot1] = colorDots;
        const [path0, path1] = getPathsForColor(color)!;

        const route = canAddPathPoint(row, col, color);
        if (route === -1) return;

        // Check if this point is adjacent to both leaders (for finishedColors logic)
        let canAdd0 = false, canAdd1 = false;
        if (path0.length === 0) {
            canAdd0 = isAdjacent({row, col}, dot0);
        } else {
            canAdd0 = isAdjacent({row, col}, path0[path0.length-1]);
        }
        if (path1.length === 0) {
            canAdd1 = isAdjacent({row, col}, dot1);
        } else {
            canAdd1 = isAdjacent({row, col}, path1[path1.length-1]);
        }

        path.push({row, col, color, route});
        renderGrid();

        if (canAdd0 && canAdd1) {
            finishedColors.add(color);
        }
    }

    function handleCellRightClick(e: MouseEvent) {
        e.preventDefault();
        const target = e.target as HTMLElement;
        const td = target.closest('td');
        if (!td) return;
        const row = parseInt(td.dataset.row!, 10);
        const col = parseInt(td.dataset.col!, 10);

        // Remove point from path (of current color)
        path = path.filter(p => !(p.row === row && p.col === col && p.color === currentColor));
        renderGrid();
    }

    colorPicker.addEventListener('change', () => {
        currentColor = colorPicker.value;
        // Only update adjacency logic, not the grid coloring
    });

    gridContainer.addEventListener('click', handleCellClick);
    gridContainer.addEventListener('contextmenu', handleCellRightClick);

    form.addEventListener('submit', () => {
        pathJsonInput.value = JSON.stringify(path);
    });

    renderGrid();
});
