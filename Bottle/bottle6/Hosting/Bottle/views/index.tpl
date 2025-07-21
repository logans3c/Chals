<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{'Welcome to the Note App' if lang != 'es' else 'Bienvenido a la aplicación de notas'}}</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/app.js"></script>
</head>
<body>
    <header>
        <h1>{{'Welcome to the Note-Taking App' if lang != 'es' else 'Bienvenido a la aplicación de notas'}}</h1>
    </header>
    <main>
        <p>{{'This application allows you to manage your notes securely.' if lang != 'es' else 'Esta aplicación te permite gestionar tus notas de forma segura.'}}</p>
        <nav>
            <ul>
                <li><a href="/register">{{'Register' if lang != 'es' else 'Registrarse'}}</a></li>
                <li><a href="/login">{{'Login' if lang != 'es' else 'Iniciar Sesión'}}</a></li>
                <li><a href="/about">{{'About' if lang != 'es' else 'Sobre'}}</a></li>
            </ul>
        </nav>
        <a href="/set-lang/en">English</a> | <a href="/set-lang/es">Español</a>
    </main>
    <footer>
        <p>&copy; 2023 Note App. All rights reserved.</p>
    </footer>
</body>
</html>