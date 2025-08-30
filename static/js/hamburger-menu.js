/* ===== FUNCIONES DEL MENÚ HAMBURGUESA RECURSIVO ===== */

// Variables globales para el estado del menú
let hamburgerMenuState = {
    isExpanded: false,
    expandedCategories: new Set(),
    expandedSubcategories: new Set()
};

function initializeHamburgerMenu() {
    console.log('🍔 Inicializando menú hamburguesa recursivo...');
    
    // Inicializar el botón hamburguesa principal
    const hamburgerToggle = document.getElementById('hamburgerToggle');
    const hamburgerContent = document.getElementById('hamburgerContent');
    
    if (hamburgerToggle && hamburgerContent) {
        hamburgerToggle.addEventListener('click', toggleHamburgerMenu);
    }
    
    // Inicializar todas las categorías y subcategorías
    initializeCategories();
    
    // Configurar responsive behavior
    setupResponsiveBehavior();
}

function initializeCategories() {
    // Inicializar categorías principales
    const categoryHeaders = document.querySelectorAll('.menu-category-header');
    categoryHeaders.forEach(header => {
        const categoryName = header.getAttribute('data-category') || 
                           header.querySelector('h5').textContent.trim();
        
        header.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleCategory(categoryName);
        });
        
        // Agregar indicador visual si tiene subcategorías
        const hasSubcategories = header.closest('.menu-section').querySelector('.subcategory');
        if (hasSubcategories) {
            const indicator = document.createElement('span');
            indicator.className = 'subcategory-indicator';
            indicator.innerHTML = '<i class="fas fa-chevron-right"></i>';
            indicator.style.cssText = 'margin-left: auto; margin-right: 10px; color: #667eea; font-size: 0.8rem;';
            header.appendChild(indicator);
        }
    });
    
    // Inicializar subcategorías recursivas
    initializeSubcategories();
}

function initializeSubcategories() {
    const subcategories = document.querySelectorAll('.subcategory .menu-category-header');
    subcategories.forEach(header => {
        const categoryName = header.getAttribute('data-category') || 
                           header.querySelector('h5').textContent.trim();
        
        header.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSubcategory(categoryName);
        });
        
        // Verificar si tiene sub-subcategorías
        const hasSubSubcategories = header.closest('.subcategory').querySelector('.subcategory');
        if (hasSubSubcategories) {
            const indicator = document.createElement('span');
            indicator.className = 'subcategory-indicator';
            indicator.innerHTML = '<i class="fas fa-chevron-right"></i>';
            indicator.style.cssText = 'margin-left: auto; margin-right: 10px; color: #667eea; font-size: 0.7rem;';
            header.appendChild(indicator);
        }
    });
}

function toggleHamburgerMenu() {
    const hamburgerToggle = document.getElementById('hamburgerToggle');
    const hamburgerContent = document.getElementById('hamburgerContent');
    
    if (hamburgerToggle && hamburgerContent) {
        hamburgerMenuState.isExpanded = !hamburgerMenuState.isExpanded;
        
        hamburgerToggle.classList.toggle('active');
        hamburgerContent.classList.toggle('expanded');
        
        console.log(`🍔 Menú hamburguesa ${hamburgerMenuState.isExpanded ? 'expandido' : 'contraído'}`);
        
        // Si se está cerrando, contraer todas las categorías
        if (!hamburgerMenuState.isExpanded) {
            collapseAllCategories();
        }
    }
}

function toggleCategory(categoryName) {
    const categoryHeader = findCategoryHeader(categoryName);
    const categoryContent = findCategoryContent(categoryName);
    const categoryIcon = findCategoryIcon(categoryName);
    
    if (categoryHeader && categoryContent && categoryIcon) {
        const isExpanded = hamburgerMenuState.expandedCategories.has(categoryName);
        
        if (isExpanded) {
            // Contraer categoría
            hamburgerMenuState.expandedCategories.delete(categoryName);
            categoryContent.classList.remove('expanded');
            categoryHeader.classList.remove('active');
            categoryIcon.classList.remove('rotated');
            
            // Contraer todas las subcategorías de esta categoría
            collapseSubcategoriesInCategory(categoryName);
        } else {
            // Expandir categoría
            hamburgerMenuState.expandedCategories.add(categoryName);
            categoryContent.classList.add('expanded');
            categoryHeader.classList.add('active');
            categoryIcon.classList.add('rotated');
        }
        
        console.log(`📁 Categoría "${categoryName}" ${isExpanded ? 'contraída' : 'expandida'}`);
    }
}

function toggleSubcategory(subcategoryName) {
    const subcategoryHeader = findSubcategoryHeader(subcategoryName);
    const subcategoryContent = findSubcategoryContent(subcategoryName);
    const subcategoryIcon = findSubcategoryIcon(subcategoryName);
    
    if (subcategoryHeader && subcategoryContent && subcategoryIcon) {
        const isExpanded = hamburgerMenuState.expandedSubcategories.has(subcategoryName);
        
        if (isExpanded) {
            // Contraer subcategoría
            hamburgerMenuState.expandedSubcategories.delete(subcategoryName);
            subcategoryContent.classList.remove('expanded');
            subcategoryHeader.classList.remove('active');
            subcategoryIcon.classList.remove('rotated');
            
            // Contraer todas las sub-subcategorías
            collapseSubSubcategoriesInSubcategory(subcategoryName);
        } else {
            // Expandir subcategoría
            hamburgerMenuState.expandedSubcategories.add(subcategoryName);
            subcategoryContent.classList.add('expanded');
            subcategoryHeader.classList.add('active');
            subcategoryIcon.classList.add('rotated');
        }
        
        console.log(`📂 Subcategoría "${subcategoryName}" ${isExpanded ? 'contraída' : 'expandida'}`);
    }
}

function expandAllCategories() {
    console.log('🔽 Expandiendo todas las categorías...');
    
    // Expandir menú principal si no está expandido
    if (!hamburgerMenuState.isExpanded) {
        toggleHamburgerMenu();
    }
    
    // Expandir todas las categorías principales
    const categoryHeaders = document.querySelectorAll('.menu-category-header');
    categoryHeaders.forEach(header => {
        const categoryName = header.getAttribute('data-category') || 
                           header.querySelector('h5').textContent.trim();
        
        if (!hamburgerMenuState.expandedCategories.has(categoryName)) {
            toggleCategory(categoryName);
        }
    });
    
    // Expandir todas las subcategorías
    const subcategoryHeaders = document.querySelectorAll('.subcategory .menu-category-header');
    subcategoryHeaders.forEach(header => {
        const subcategoryName = header.getAttribute('data-category') || 
                              header.querySelector('h5').textContent.trim();
        
        if (!hamburgerMenuState.expandedSubcategories.has(subcategoryName)) {
            toggleSubcategory(subcategoryName);
        }
    });
}

function collapseAllCategories() {
    console.log('🔼 Contrayendo todas las categorías...');
    
    // Limpiar estados
    hamburgerMenuState.expandedCategories.clear();
    hamburgerMenuState.expandedSubcategories.clear();
    
    // Contraer todas las categorías principales
    const categoryContents = document.querySelectorAll('.menu-category-content');
    const categoryHeaders = document.querySelectorAll('.menu-category-header');
    const categoryIcons = document.querySelectorAll('.category-icon');
    
    categoryContents.forEach(content => content.classList.remove('expanded'));
    categoryHeaders.forEach(header => header.classList.remove('active'));
    categoryIcons.forEach(icon => icon.classList.remove('rotated'));
    
    // Contraer todas las subcategorías
    const subcategoryContents = document.querySelectorAll('.subcategory .menu-category-content');
    const subcategoryHeaders = document.querySelectorAll('.subcategory .menu-category-header');
    const subcategoryIcons = document.querySelectorAll('.subcategory .category-icon');
    
    subcategoryContents.forEach(content => content.classList.remove('expanded'));
    subcategoryHeaders.forEach(header => header.classList.remove('active'));
    subcategoryIcons.forEach(icon => icon.classList.remove('rotated'));
}

function collapseSubcategoriesInCategory(categoryName) {
    const categoryElement = findCategoryElement(categoryName);
    if (categoryElement) {
        const subcategories = categoryElement.querySelectorAll('.subcategory .menu-category-content');
        const subcategoryHeaders = categoryElement.querySelectorAll('.subcategory .menu-category-header');
        const subcategoryIcons = categoryElement.querySelectorAll('.subcategory .category-icon');
        
        subcategories.forEach(content => {
            content.classList.remove('expanded');
            const subcategoryName = content.closest('.subcategory').querySelector('.menu-category-header h5').textContent.trim();
            hamburgerMenuState.expandedSubcategories.delete(subcategoryName);
        });
        
        subcategoryHeaders.forEach(header => header.classList.remove('active'));
        subcategoryIcons.forEach(icon => icon.classList.remove('rotated'));
    }
}

function collapseSubSubcategoriesInSubcategory(subcategoryName) {
    const subcategoryElement = findSubcategoryElement(subcategoryName);
    if (subcategoryElement) {
        const subSubcategories = subcategoryElement.querySelectorAll('.subcategory .menu-category-content');
        const subSubcategoryHeaders = subcategoryElement.querySelectorAll('.subcategory .menu-category-header');
        const subSubcategoryIcons = subcategoryElement.querySelectorAll('.subcategory .category-icon');
        
        subSubcategories.forEach(content => {
            content.classList.remove('expanded');
            const subSubcategoryName = content.closest('.subcategory').querySelector('.menu-category-header h5').textContent.trim();
            hamburgerMenuState.expandedSubcategories.delete(subSubcategoryName);
        });
        
        subSubcategoryHeaders.forEach(header => header.classList.remove('active'));
        subSubcategoryIcons.forEach(icon => icon.classList.remove('rotated'));
    }
}

// Funciones auxiliares para encontrar elementos
function findCategoryHeader(categoryName) {
    return Array.from(document.querySelectorAll('.menu-category-header')).find(header => {
        const headerText = header.querySelector('h5').textContent.trim();
        return headerText === categoryName && !header.closest('.subcategory');
    });
}

function findCategoryContent(categoryName) {
    const categoryElement = findCategoryElement(categoryName);
    return categoryElement ? categoryElement.querySelector('.menu-category-content') : null;
}

function findCategoryIcon(categoryName) {
    const categoryHeader = findCategoryHeader(categoryName);
    return categoryHeader ? categoryHeader.querySelector('.category-icon') : null;
}

function findCategoryElement(categoryName) {
    const categoryHeader = findCategoryHeader(categoryName);
    return categoryHeader ? categoryHeader.closest('.menu-section') : null;
}

function findSubcategoryHeader(subcategoryName) {
    return Array.from(document.querySelectorAll('.subcategory .menu-category-header')).find(header => {
        const headerText = header.querySelector('h5').textContent.trim();
        return headerText === subcategoryName;
    });
}

function findSubcategoryContent(subcategoryName) {
    const subcategoryElement = findSubcategoryElement(subcategoryName);
    return subcategoryElement ? subcategoryElement.querySelector('.menu-category-content') : null;
}

function findSubcategoryIcon(subcategoryName) {
    const subcategoryHeader = findSubcategoryHeader(subcategoryName);
    return subcategoryHeader ? subcategoryHeader.querySelector('.category-icon') : null;
}

function findSubcategoryElement(subcategoryName) {
    const subcategoryHeader = findSubcategoryHeader(subcategoryName);
    return subcategoryHeader ? subcategoryHeader.closest('.subcategory') : null;
}

function setupResponsiveBehavior() {
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            // En móviles, contraer automáticamente algunas categorías para ahorrar espacio
            if (hamburgerMenuState.expandedCategories.size > 2) {
                const expandedCategories = Array.from(hamburgerMenuState.expandedCategories);
                expandedCategories.slice(2).forEach(categoryName => {
                    if (hamburgerMenuState.expandedCategories.has(categoryName)) {
                        toggleCategory(categoryName);
                    }
                });
            }
        }
    });
}

function addMenuHoverEffects() {
    // Agregar efectos de hover a las categorías del menú
    const menuSections = document.querySelectorAll('.menu-section');
    menuSections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
}

// ===== FUNCIONES PARA JUMBOTRON DE MENSAJES =====

function showJumbotronMessage(title, message, type = 'info', actions = []) {
    const jumbotronContainer = document.querySelector('.jumbotron-container') || createJumbotronContainer();
    
    const jumbotronHTML = `
        <div class="jumbotron-message jumbotron-${type}" id="jumbotron-${Date.now()}">
            <button class="jumbotron-close" onclick="closeJumbotron(this)">
                <i class="fas fa-times"></i>
            </button>
            <div class="jumbotron-header">
                <div class="icon">
                    ${getJumbotronIcon(type)}
                </div>
                <h2>${title}</h2>
            </div>
            <div class="jumbotron-content">
                <p>${message}</p>
                ${actions.length > 0 ? `
                    <div class="jumbotron-actions">
                        ${actions.map(action => `
                            <a href="${action.url || '#'}" class="btn" onclick="${action.onclick || ''}">
                                <i class="${action.icon || 'fas fa-arrow-right'}"></i>
                                ${action.text}
                            </a>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    jumbotronContainer.insertAdjacentHTML('beforeend', jumbotronHTML);
    
    // Animación de entrada
    const newJumbotron = jumbotronContainer.lastElementChild;
    newJumbotron.style.opacity = '0';
    newJumbotron.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        newJumbotron.style.transition = 'all 0.3s ease';
        newJumbotron.style.opacity = '1';
        newJumbotron.style.transform = 'translateY(0)';
    }, 10);
    
    console.log(`💬 Jumbotron mostrado: ${title}`);
}

function closeJumbotron(closeButton) {
    const jumbotron = closeButton.closest('.jumbotron-message');
    
    jumbotron.style.transition = 'all 0.3s ease';
    jumbotron.style.opacity = '0';
    jumbotron.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        jumbotron.remove();
    }, 300);
}

function createJumbotronContainer() {
    const container = document.createElement('div');
    container.className = 'jumbotron-container';
    document.body.insertBefore(container, document.body.firstChild);
    return container;
}

function getJumbotronIcon(type) {
    const icons = {
        'success': '<i class="fas fa-check-circle"></i>',
        'warning': '<i class="fas fa-exclamation-triangle"></i>',
        'danger': '<i class="fas fa-times-circle"></i>',
        'info': '<i class="fas fa-info-circle"></i>'
    };
    return icons[type] || icons['info'];
}

// Funciones de utilidad para mostrar mensajes específicos
function showSuccessMessage(title, message, actions = []) {
    showJumbotronMessage(title, message, 'success', actions);
}

function showWarningMessage(title, message, actions = []) {
    showJumbotronMessage(title, message, 'warning', actions);
}

function showErrorMessage(title, message, actions = []) {
    showJumbotronMessage(title, message, 'danger', actions);
}

function showInfoMessage(title, message, actions = []) {
    showJumbotronMessage(title, message, 'info', actions);
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeHamburgerMenu();
    addMenuHoverEffects();
    
    // Mostrar mensaje de bienvenida
    setTimeout(() => {
        showInfoMessage(
            '🎯 Sistema OTIF Master',
            'Bienvenido al sistema de procesamiento OTIF. El menú hamburguesa recursivo está listo para usar.',
            [
                {
                    text: 'Expandir Todo',
                    icon: 'fas fa-expand-alt',
                    onclick: 'expandAllCategories()'
                },
                {
                    text: 'Contraer Todo',
                    icon: 'fas fa-compress-alt',
                    onclick: 'collapseAllCategories()'
                }
            ]
        );
    }, 1000);
});

// Event listener para redimensionamiento de ventana
window.addEventListener('resize', function() {
    // Ajustar comportamiento responsive
    if (window.innerWidth <= 768) {
        // En móviles, asegurar que el menú no ocupe demasiado espacio
        const hamburgerContent = document.getElementById('hamburgerContent');
        if (hamburgerContent && hamburgerContent.classList.contains('expanded')) {
            hamburgerContent.style.maxHeight = '60vh';
        }
    }
});

