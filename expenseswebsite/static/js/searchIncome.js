const searchField = document.querySelector('#searchField');
const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector('.pagination-container');
const tableBody = document.querySelector('.table-body');
const noResults = document.querySelector('.no_results');

tableOutput.style.display = 'none'; 

searchField.addEventListener('keyup', (e)=>{
    const searchValue = e.target.value;

    if (searchValue.trim().length>0){
        paginationContainer.style.display = 'none';
        console.log('searchValue',searchValue)

        tableBody.innerHTML = '';

        fetch("/income/search-income/", {
            body: JSON.stringify({ searchText: searchValue }),
            method: 'POST',
    
        })
            .then(res => res.json())
            .then(data => {
               console.log('data',data)
               tableOutput.style.display = 'block';
               appTable.style.display = 'none';

               

               if(data.length===0){
                noResults.style.display = 'block';
                tableOutput.style.display = 'none';

               }else{
                noResults.style.display = 'none';
                data.forEach((item) => {
                    tableBody.innerHTML +=   `
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.description}</td>
                            <td>${item.source}</td>
                            <td>${item.date}</td>
                        </tr>
                    `
                    // console.log('item',item)

                });


               }
            });
    }else {
        tableOutput.style.display = 'none';
        paginationContainer.style.display = 'block';
        appTable.style.display = 'block';

    }
}); 