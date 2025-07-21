<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{'Login' if lang != 'es' else 'Iniciar Sesión'}}</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/app.js"></script>
</head>
<body>
    <div class="container">
        <h2>{{'Login' if lang != 'es' else 'Iniciar Sesión'}}</h2>
        % if message:
            <div style="color: red; margin-bottom: 10px;">{{message if lang != 'es' else 'Usuario o contraseña inválidos.'}}</div>
        % end
        <form action="/login" method="post">
            <div class="form-group">
                <label for="username">{{'Username:' if lang != 'es' else 'Usuario:'}}</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">{{'Password:' if lang != 'es' else 'Contraseña:'}}</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">{{'Login' if lang != 'es' else 'Iniciar Sesión'}}</button>
        </form>
        <p>{{"Don't have an account?" if lang != 'es' else '¿No tienes una cuenta?'}} <a href="/register">{{'Register here' if lang != 'es' else 'Regístrate aquí'}}</a></p>
        <p><a href="/about">{{'About this app' if lang != 'es' else 'Sobre esta aplicación'}}</a></p>
        <a href="/set-lang/en">English</a> | <a href="/set-lang/es">Español</a>
    </div>
</body>
</html>