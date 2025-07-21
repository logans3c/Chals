<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{'Register' if lang != 'es' else 'Registrarse'}}</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/app.js"></script>
</head>
<body>
    <div class="container">
        <h1>{{'Register' if lang != 'es' else 'Registrarse'}}</h1>
        % if message:
            <div style="color: {{'green' if success else 'red'}}; margin-bottom: 10px;">
                % if lang == 'es':
                    % if success:
                        ¡Registro exitoso! Por favor inicia sesión.
                    % elif 'exists' in message:
                        El usuario ya existe.
                    % else:
                        Usuario y contraseña requeridos.
                    % end
                % else:
                    % if success:
                        Registration successful! Please log in.
                    % elif 'exists' in message:
                        Username already exists.
                    % else:
                        Username and password are required.
                    % end
                % end
            </div>
        % end
        <form action="/register" method="post">
            <label for="username">{{'Username:' if lang != 'es' else 'Usuario:'}}</label>
            <input type="text" id="username" name="username" required>

            <label for="password">{{'Password:' if lang != 'es' else 'Contraseña:'}}</label>
            <input type="password" id="password" name="password" required>

            <button type="submit">{{'Create Account' if lang != 'es' else 'Crear Cuenta'}}</button>
        </form>
        <p>{{'Already have an account?' if lang != 'es' else '¿Ya tienes una cuenta?'}} <a href="/login">{{'Login here' if lang != 'es' else 'Inicia sesión aquí'}}</a>.</p>
        <a href="/set-lang/en">English</a> | <a href="/set-lang/es">Español</a>
    </div>
</body>
</html>