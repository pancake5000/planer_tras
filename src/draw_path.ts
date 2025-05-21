// Use a unique type name to avoid conflicts with edit_board.ts
type PathDot = { row: number, col: number, color: string };
type PathPoint = { row: number, col: number, color: string };

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

    function canAddPathPoint(row: number, col: number, color: string): boolean {
        // Don't allow duplicate points in path for this color
        if (path.some(p => p.row === row && p.col === col && p.color === color)) return false;
        // Only allow if adjacent to path/dot of this color
        return isAdjacentToPathOrDot(row, col, color);
    }

    function handleCellClick(e: MouseEvent) {
        const target = e.target as HTMLElement;
        const td = target.closest('td');
        if (!td) return;
        const row = parseInt(td.dataset.row!, 10);
        const col = parseInt(td.dataset.col!, 10);

        if (!canAddPathPoint(row, col, currentColor)) return;
        path.push({row, col, color: currentColor});
        renderGrid();
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
