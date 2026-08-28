document.addEventListener('DOMContentLoaded', function() {
            const toggle = document.getElementById('mobile-toggle');
            const nav = document.getElementById('nav-content');
            const dropdownTrigger = document.querySelector('.dropdown-trigger');

            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                nav.classList.toggle('active');
                toggle.classList.toggle('active');
                document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
            });

            dropdownTrigger.addEventListener('click', function(e) {
                if (window.innerWidth <= 992) {
                    e.preventDefault();
                    this.parentElement.classList.toggle('mobile-open');
                }
            });

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

document.addEventListener('DOMContentLoaded', function () {
        const toggleBtn = document.getElementById('toggleSearchBtn');
        const searchSection = document.getElementById('servicesSearch');

        toggleBtn.addEventListener('click', function () {
            searchSection.classList.toggle('is-hidden');

            if (searchSection.classList.contains('is-hidden')) {
                toggleBtn.textContent = 'Покажи търсачката и филтрите';
            } else {
                toggleBtn.textContent = 'Скрий';
            }
        });
    });

document.querySelector('input[type="file"]').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file || !file.type.startsWith('image/')) return;

    // Прескачаме компресията, ако файлът вече е малък (напр. под 1 MB)
    if (file.size < 1024 * 1024) return;

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function(event) {
        const img = new Image();
        img.src = event.target.result;
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const MAX_WIDTH = 1920;
            const MAX_HEIGHT = 1920;
            let width = img.width;
            let height = img.height;

            if (width > height) {
                if (width > MAX_WIDTH) {
                    height *= MAX_WIDTH / width;
                    width = MAX_WIDTH;
                }
            } else {
                if (height > MAX_HEIGHT) {
                    width *= MAX_HEIGHT / height;
                    height = MAX_HEIGHT;
                }
            }

            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob(function(blob) {
                // Заменяме файла във формата с новия компресиран файл
                const newFile = new File([blob], file.name.replace(/\.[^/.]+$/, "") + ".jpg", {
                    type: 'image/jpeg',
                    lastModified: Date.now()
                });

                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                e.target.files = dataTransfer.files;
            }, 'image/jpeg', 0.8); // 80% качество
        };
    };
});



