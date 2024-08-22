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
                window.location.href = '/login.html';
            });
        } else {
            usernameElement.textContent = 'Usuario no autenticado';
            logoutButton.textContent = 'Login'; // Cambia el texto del botón a "Login"
            logoutButton.addEventListener('click', function() {
                window.location.href = '/login.html';
            });
        }
    }

    updateUI();
});
