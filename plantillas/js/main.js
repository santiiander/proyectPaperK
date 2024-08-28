document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    updateUI(); // Actualiza la UI al cargar la página
});

// Función para obtener el token del almacenamiento local
function getToken() {
    const token = localStorage.getItem('access_token');
    console.log('Token:', token); // Añade esto para verificar el token
    return token;
}


// Función para cargar los proyectos desde el backend
function loadProjects() {
    fetch("http://localhost:8000/proyectos/proyectos/traer", {
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(projects => {
        const container = document.getElementById('projectsContainer');
        container.innerHTML = ''; // Limpia el contenedor antes de agregar los nuevos proyectos

        if (!Array.isArray(projects)) {
            throw new Error("La respuesta no es un array de proyectos.");
        }

        projects.forEach(project => {
            const projectDiv = document.createElement('div');
            projectDiv.className = 'paper';
            projectDiv.innerHTML = `
                <h2>${project.nombre}</h2>
                <img src="http://localhost:8000/${project.imagen}" alt="Imagen del Proyecto" class="project-image">
                <p>${project.descripcion}</p>
            `;
            container.appendChild(projectDiv);
        });
    })
    .catch(error => console.error('Error al cargar los proyectos:', error));
}

// Función para crear un nuevo proyecto
function createProject() {
    const form = document.querySelector('#proyectoForm');
    const formData = new FormData(form);

    fetch("http://localhost:8000/proyectos/proyectos/", {
        method: "POST",
        body: formData,
        headers: {
            "Authorization": `Bearer ${getToken()}`,
            "Content-Type": "multipart/form-data" // Asegúrate de que esto sea correcto para tu backend
        }
    })
    .then(response => {
        if (response.ok) {
            alert("Proyecto creado exitosamente");
            closePopup();
            loadProjects(); // Recargar proyectos para ver el nuevo
        } else {
            return response.json().then(result => {
                throw new Error(result.detail || 'Error creating project');
            });
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Hubo un problema con el envío del formulario.");
    });
}

// Función para mostrar el popup de creación de proyecto
function openPopup() {
    document.getElementById("popupForm").style.display = "block";
}

// Función para cerrar el popup de creación de proyecto
function closePopup() {
    document.getElementById("popupForm").style.display = "none";
}

// Función para manejar el envío del formulario de creación de proyecto
document.querySelector('#proyectoForm').addEventListener('submit', event => {
    event.preventDefault();
    if (!getToken()) {
        alert("Por favor, inicia sesión para crear un proyecto.");
        return;
    }
    createProject();
});

// Función para actualizar la UI al cargar la página
function updateUI() {
    const usernameElement = document.getElementById('username');
    const logoutButton = document.getElementById('logoutButton');

    function updateUIComponents() {
        const username = getUsername();
        if (username) {
            usernameElement.textContent = username;
            logoutButton.textContent = 'Logout';
            logoutButton.addEventListener('click', function() {
                localStorage.removeItem('username');
                localStorage.removeItem('access_token');
                window.location.href = '/plantillas/login.html';
            });
        } else {
            usernameElement.textContent = 'Usuario no autenticado';
            logoutButton.textContent = 'Login';
            logoutButton.addEventListener('click', function() {
                window.location.href = '/plantillas/login.html';
            });
        }
    }

    updateUIComponents();
}

// Función para obtener el nombre del usuario del almacenamiento local
function getUsername() {
    return localStorage.getItem('username');
}

// Función para manejar el login del usuario
function handleLoginResponse(response) {
    if (response.ok) {
        return response.json();
    } else {
        throw new Error('Login failed');
    }
}

// Función para iniciar sesión
function login() {
    const formData = new FormData(document.querySelector('#loginForm'));

    fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        body: formData
    })
    .then(handleLoginResponse)
    .then(data => {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('username', data.email); // O cualquier otro identificador del usuario
        alert('Login successful!');
        window.location.href = '/plantillas/index.html'; // Redirige a la página principal
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to login');
    });
}

// Función para rotar la imagen del perfil al hacer scroll
document.addEventListener('scroll', function() {
    const image = document.querySelector('.profile-image');
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    image.style.transform = `rotate(${scrollTop / 2}deg)`; // Ajusta la rotación según la velocidad deseada
});
