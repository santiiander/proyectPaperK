document.addEventListener('DOMContentLoaded', () => {
    loadUserProjects();
    updateUserUI(); // Actualiza la UI al cargar la página
});

// Función para obtener el token del almacenamiento local
function getToken() {
    return localStorage.getItem('access_token');
}

// Función para cargar los proyectos del usuario desde el backend
function loadUserProjects() {
    fetch("http://localhost:8000/proyectos/proyectos/mi-proyecto", { // Supongo que esta sería la ruta para cargar proyectos de un usuario
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
        const container = document.getElementById('userProjectsContainer');
        container.innerHTML = ''; // Limpia el contenedor antes de agregar los nuevos proyectos

        if (!Array.isArray(projects)) {
            throw new Error("La respuesta no es un array de proyectos.");
        }

        projects.forEach(project => {
            const projectDiv = document.createElement('div');
            projectDiv.className = 'project-item';
            projectDiv.dataset.pdfPath = project.archivo_pdf;

            projectDiv.innerHTML = `
                <h2>${project.nombre}</h2>
                <img src="http://localhost:8000/${project.imagen}" alt="Imagen del Proyecto" class="project-image">
                <p>${project.descripcion}</p>
                <button class="download-button" onclick="downloadPDF('${project.archivo_pdf}')"></button>
            `;
            container.appendChild(projectDiv);
        });
    })
    .catch(error => console.error('Error al cargar los proyectos:', error));
}

// Función para descargar el archivo PDF
function downloadPDF(pdfPath) {
    const url = `http://localhost:8000/${pdfPath}`;

    fetch(url, {
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const link = document.createElement('a');
        const url = window.URL.createObjectURL(blob);
        link.href = url;
        link.download = pdfPath.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    })
    .catch(error => console.error('Error al descargar el PDF:', error));
}

// Función para actualizar la UI del usuario
function updateUserUI() {
    const emailElement = document.getElementById('userEmail');
    const logoutButton = document.getElementById('logoutButton');

    function updateUIComponents() {
        const userEmail = getUserEmail();
        if (userEmail) {
            emailElement.textContent = userEmail;
            logoutButton.textContent = 'Logout';
            logoutButton.addEventListener('click', function() {
                localStorage.removeItem('username');
                localStorage.removeItem('access_token');
                window.location.href = '/plantillas/login.html';
            });
        } else {
            emailElement.textContent = 'Usuario no autenticado';
            logoutButton.textContent = 'Login';
            logoutButton.addEventListener('click', function() {
                window.location.href = '/plantillas/login.html';
            });
        }
    }

    updateUIComponents();
}

// Función para obtener el correo electrónico del usuario del almacenamiento local
function getUserEmail() {
    return localStorage.getItem('username');
}
