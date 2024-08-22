document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Evita el envío del formulario tradicional

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    console.log('Email:', email);
    console.log('Password:', password);

    try {
        const response = await fetch('http://localhost:8000/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'username': email,
                'password': password
            })
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Response data:', data);

        localStorage.setItem('access_token', data.access_token); // Guarda el token en el almacenamiento local
        localStorage.setItem('username', email); // Guarda el nombre de usuario en el almacenamiento local

        // Redirige a la página principal o realiza cualquier otra acción necesaria
        window.location.href = '/';
    } catch (error) {
        console.error('Error:', error);
        alert('Error de autenticación. Por favor, verifica tus credenciales.');
    }
});
