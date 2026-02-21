document.addEventListener('DOMContentLoaded', function() {
            const toggle = document.getElementById('mobile-toggle');
            const nav = document.getElementById('nav-content');
            const dropdownTrigger = document.querySelector('.dropdown-trigger');

            // Отваряне/Затваряне на мобилно меню
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                nav.classList.toggle('active');
                toggle.classList.toggle('active');
                document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
            });

            // Работа на Dropdown на мобилни устройства (клик)
            dropdownTrigger.addEventListener('click', function(e) {
                if (window.innerWidth <= 992) {
                    e.preventDefault();
                    this.parentElement.classList.toggle('mobile-open');
                }
            });

            // Затваряне при клик извън менюто
            document.addEventListener('click', function(e) {
                if (!nav.contains(e.target) && !toggle.contains(e.target)) {
                    nav.classList.remove('active');
                    toggle.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        });

document.querySelectorAll('form[class$="-delete-form"]').forEach(element => element.addEventListener('submit', function(event) {
        const confirmed = confirm('Сигурни ли сте, че искате да изтриете този запис?');

        if (!confirmed) {
            event.preventDefault();
        }
    }));




