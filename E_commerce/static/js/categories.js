// categories.js
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/category/') // Ensure the correct URL for your API endpoint
        .then(response => response.json())
        .then(data => {
            const categoryList = document.getElementById('category-list');
            data.forEach(category => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<a class="dropdown-item" href="/productfilter/${category.category_id}">${category.category}</a>`;
                categoryList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching categories:', error);
        });
});