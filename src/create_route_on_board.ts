// Use a unique type name to avoid conflicts with edit_board.ts
type RouteDot = { row: number, col: number, color: string };
type RoutePoint = { row: number, col: number };

window.addEventListener('DOMContentLoaded', () => {
    const rows = (window as any).CREATE_ROUTE_BOARD_ROWS as number;
    const cols = (window as any).CREATE_ROUTE_BOARD_COLS as number;
    const dots: RouteDot[] = (window as any).CREATE_ROUTE_DOTS || [];
    let route: RoutePoint[] = [];

    const gridContainer = document.getElementById('grid-container') as HTMLElement;
    const routeJsonInput = document.getElementById('route-json') as HTMLInputElement;
    const form = document.getElementById('route-form') as HTMLFormElement;

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

                // Draw route index if present
                const idx = route.findIndex(p => p.row === r && p.col === c);
                if (idx !== -1) {
                    td.style.background = '#ffe';
                    td.innerHTML += `<span style="font-size:0.8em;color:#333;">${idx + 1}</span>`;
                }

                tr.appendChild(td);
            }
            table.appendChild(tr);
        }
        gridContainer.appendChild(table);
    }

    function handleCellClick(e: MouseEvent) {
        const target = e.target as HTMLElement;
        const td = target.closest('td');
        if (!td) return;
        const row = parseInt(td.dataset.row!, 10);
        const col = parseInt(td.dataset.col!, 10);

        // Don't allow duplicate points in route
        if (route.some(p => p.row === row && p.col === col)) return;
        route.push({row, col});
        renderGrid();
    }

    function handleCellRightClick(e: MouseEvent) {
        e.preventDefault();
        const target = e.target as HTMLElement;
        const td = target.closest('td');
        if (!td) return;
        const row = parseInt(td.dataset.row!, 10);
        const col = parseInt(td.dataset.col!, 10);

        // Remove point from route
        route = route.filter(p => !(p.row === row && p.col === col));
        renderGrid();
    }

    gridContainer.addEventListener('click', handleCellClick);
    gridContainer.addEventListener('contextmenu', handleCellRightClick);

    form.addEventListener('submit', () => {
        routeJsonInput.value = JSON.stringify(route);
    });

    renderGrid();
});
