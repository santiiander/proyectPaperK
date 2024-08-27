document.addEventListener('scroll', function() {
    const image = document.querySelector('.profile-image');
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    image.style.transform = `rotate(${scrollTop / 2}deg)`; // Ajusta la rotación según la velocidad deseada
});

function openPopup() {
    document.getElementById("popupForm").style.display = "block";
}

function closePopup() {
    document.getElementById("popupForm").style.display = "none";
}

document.addEventListener('DOMContentLoaded', function() {
    const usernameElement = document.getElementById('username');
    const logoutButton = document.getElementById('logoutButton');

    function getUsername() {
        return localStorage.getItem('username');
    }

    function updateUI() {
        const username = getUsername();
        if (username) {
            usernameElement.textContent = username;
            logoutButton.textContent = 'Logout'; // Cambia el texto del botón a "Logout"
            logoutButton.addEventListener('click', function() {
                localStorage.removeItem('username');
                localStorage.removeItem('access_token'); // Opcional, si también quieres limpiar el token
                window.location.href = '/plantillas/login.html';
            });
        } else {
            usernameElement.textContent = 'Usuario no autenticado';
            logoutButton.textContent = 'Login'; // Cambia el texto del botón a "Login"
            logoutButton.addEventListener('click', function() {
                window.location.href = '/plantillas/login.html';
            });
        }
    }

    updateUI();
});

document.addEventListener("DOMContentLoaded", function() {
    const popup = document.querySelector(".popup-form");
    const openPopupBtn = document.querySelector("#openPopup"); // Botón para abrir el popup
    const closePopupBtn = document.querySelector(".close"); // Botón para cerrar el popup
    const form = document.querySelector("#proyectoForm");

    // Función para abrir el popup
    function openPopup() {
        popup.style.display = "flex";
    }

    // Función para cerrar el popup
    function closePopup() {
        popup.style.display = "none";
    }

    // Función para verificar si el usuario está loggeado
    function isUserLoggedIn() {
        return localStorage.getItem('access_token') !== null;
    }

    // Mostrar el popup cuando se haga clic en el botón de abrir
    if (openPopupBtn) {
        openPopupBtn.addEventListener("click", openPopup);
    }

    // Cerrar el popup cuando se haga clic en el botón de cerrar
    if (closePopupBtn) {
        closePopupBtn.addEventListener("click", closePopup);
    }

    // Enviar el formulario cuando se envíe
    if (form) {
        form.addEventListener("submit", async function(event) {
            event.preventDefault(); // Evita el envío por defecto del formulario

            // Verificar si el usuario está loggeado
            if (!isUserLoggedIn()) {
                alert("Por favor, inicia sesión para crear un proyecto.");
                return; // Evita el envío del formulario
            }

            const formData = new FormData(form);

            try {
                const response = await fetch("http://localhost:8000/proyectos/proyectos", {
                    method: "POST",
                    body: formData,
                });

                if (response.ok) {
                    alert("Proyecto creado exitosamente");
                    closePopup();
                } else {
                    const result = await response.json();
                    alert(`Error: ${result.detail}`);
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Hubo un problema con el envío del formulario.");
            }
        });
    }
});
