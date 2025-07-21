<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{'About - Note App' if lang != 'es' else 'Sobre - Aplicación de Notas'}}</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/app.js"></script>
</head>
<body>
    <header>
        <h1>{{'About This Application' if lang != 'es' else 'Sobre esta aplicación'}}</h1>
    </header>
    <main>
        <section>
            <h2>{{'Welcome to the Note-Taking App' if lang != 'es' else 'Bienvenido a la aplicación de notas'}}</h2>
            <p>{{'This application allows users to securely register, log in, and manage their personal notes.' if lang != 'es' else 'Esta aplicación permite a los usuarios registrarse, iniciar sesión y gestionar sus notas personales de forma segura.'}}</p>
            <p>{{'Features include:' if lang != 'es' else 'Características:'}}</p>
            <ul>
                <li>{{'User registration and authentication' if lang != 'es' else 'Registro y autenticación de usuarios'}}</li>
                <li>{{'Add, view, and manage personal notes' if lang != 'es' else 'Agregar, ver y gestionar notas personales'}}</li>
                <li>{{'Admin panel for managing users and notes' if lang != 'es' else 'Panel de administración para gestionar usuarios y notas'}}</li>
            </ul>
            <p>{{'To get started, please register or log in to your account.' if lang != 'es' else 'Para comenzar, por favor regístrate o inicia sesión en tu cuenta.'}}</p>
        </section>
        <a href="/set-lang/en">English</a> | <a href="/set-lang/es">Español</a>
    </main>
    <footer>
        <p>&copy; 2023 Note App. All rights reserved.</p>
    </footer>
</body>
</html>