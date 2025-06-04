type Dot = { row: number, col: number, color: string };

window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('board-form') as HTMLFormElement;
    const rowsInput = document.getElementById('id_rows') as HTMLInputElement;
    const colsInput = document.getElementById('id_cols') as HTMLInputElement;
    const gridContainer = document.getElementById('grid-container') as HTMLElement;
    const colorPicker = document.getElementById('color-picker') as HTMLSelectElement;
    const addPairBtn = document.getElementById('add-pair-btn') as HTMLButtonElement;
    const dotsJsonInput = document.getElementById('dots-json') as HTMLInputElement;

    let rows = parseInt(rowsInput.value, 10) || 5;
    let cols = parseInt(colsInput.value, 10) || 5;
    let dots: Dot[] = (window as any).INIT_DOTS || [];
    let pairColor: string = colorPicker.value;
    let pairClicks: {row: number, col: number}[] = [];
    let addingPair = false;

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
                tr.appendChild(td);
            }
            table.appendChild(tr);
        }
        gridContainer.appendChild(table);
    }

    function renderPairs() {
        // Find the pairs table by a unique selector (not just any table)
        const pairsTable = document.querySelector('table[data-pairs-table]') as HTMLTableElement;
        if (!pairsTable) return;

        // Remove all rows except the header (first row)
        while (pairsTable.rows.length > 1) {
            pairsTable.deleteRow(1);
        }

        // Group dots by color to form pairs
        const colorMap: { [color: string]: Dot[] } = {};
        dots.forEach(dot => {
            if (!colorMap[dot.color]) colorMap[dot.color] = [];
            colorMap[dot.color].push(dot);
        });

        Object.keys(colorMap).forEach(color => {
            const pair = colorMap[color];
            if (pair.length === 2) {
                const tr = document.createElement('tr');

                // Color cell
                const colorTd = document.createElement('td');
                const colorSpan = document.createElement('span');
                colorSpan.style.display = 'inline-block';
                colorSpan.style.width = '24px';
                colorSpan.style.height = '24px';
                colorSpan.style.borderRadius = '50%';
                colorSpan.style.background = color;
                colorTd.appendChild(colorSpan);
                tr.appendChild(colorTd);

                // Point 1 cell
                const point1Td = document.createElement('td');
                point1Td.textContent = `(${pair[0].row}, ${pair[0].col})`;
                tr.appendChild(point1Td);

                // Point 2 cell
                const point2Td = document.createElement('td');
                point2Td.textContent = `(${pair[1].row}, ${pair[1].col})`;
                tr.appendChild(point2Td);

                // Delete button cell
                const deleteTd = document.createElement('td');
                const deleteForm = document.createElement('form');
                deleteForm.method = 'post';
                deleteForm.style.display = 'inline';
                deleteForm.innerHTML = `
                    <input type="hidden" name="delete_pair_color" value="${color}">
                    <button type="submit">Usuń parę</button>
                `;
                const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement;
                if (csrfToken) {
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = csrfToken.value;
                    deleteForm.appendChild(csrfInput);
                }
                deleteTd.appendChild(deleteForm);
                tr.appendChild(deleteTd);

                pairsTable.appendChild(tr);
            }
        });
        updateAddPairBtnState();
    }

    function canAddDot(row: number, col: number, color: string): boolean {
        if (dots.find(dot => dot.row === row && dot.col === col)) return false;
        if (dots.filter(dot => dot.color === color).length >= 2) return false;
        return true;
    }

    function handleCellClick(e: MouseEvent) {
        const target = e.target as HTMLElement;
        const td = target.closest('td');
        if (!td) return;
        const row = parseInt(td.dataset.row!, 10);
        const col = parseInt(td.dataset.col!, 10);
        if (!canAddDot(row, col, pairColor)) return;
        pairClicks.push({row, col});
        dots.push({row, col, color: pairColor});
        renderGrid();
        renderPairs(); // Update the pairs list immediately after adding a dot
        updateAddPairBtnState();
        if (dots.filter(dot => dot.color === pairColor).length === 2) {
            addPairBtn.disabled = true;
            colorPicker.disabled = false;
            pairClicks = [];
        } else {
            addPairBtn.disabled = true;
            colorPicker.disabled = true;
        }
    }

    function handleAddPair() {
        pairClicks = [];
        pairColor = colorPicker.value;
        addPairBtn.disabled = true;
        colorPicker.disabled = true;
    }

    function handleRemoveDot(row: number, col: number) {
        dots = dots.filter(dot => !(dot.row === row && dot.col === col));
        renderGrid();
    }

    function updateDims() {
        rows = parseInt(rowsInput.value, 10) || 5;
        cols = parseInt(colsInput.value, 10) || 5;
        dots = dots.filter(dot => dot.row < rows && dot.col < cols);
        renderGrid();
    }

    function isColorUsed(color: string): boolean {
        return dots.filter(dot => dot.color === color).length === 2;
    }

    function updateAddPairBtnState() {
        // Disable addPairBtn if color is already used
        if (isColorUsed(pairColor)) {
            addPairBtn.disabled = true;
        } else {
            addPairBtn.disabled = false;
        }
    }

    colorPicker.addEventListener('change', () => {
        pairColor = colorPicker.value;
        updateAddPairBtnState();
    });

    addPairBtn.addEventListener('click', handleAddPair);

    gridContainer.addEventListener('click', handleCellClick);

    rowsInput.addEventListener('input', updateDims);
    colsInput.addEventListener('input', updateDims);

    form.addEventListener('submit', (e) => {
        if(colorPicker.disabled){
            e.preventDefault();
            return;
        }
        dotsJsonInput.value = JSON.stringify(dots);
    });

    renderGrid();
    renderPairs();
    updateAddPairBtnState();
});
