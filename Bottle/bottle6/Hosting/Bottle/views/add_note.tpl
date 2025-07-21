<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{'Add Note' if lang != 'es' else 'Agregar Nota'}}</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/app.js"></script>
    <style>
        .note-preview {
            background: #f9f9f9;
            border-radius: 8px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.07);
            margin: 12px 0;
            padding: 16px 18px;
            border-left: 5px solid #45a049;
            transition: box-shadow 0.2s;
            word-break: break-word;
        }
        .note-preview:hover {
            box-shadow: 0 2px 12px rgba(69,160,73,0.13);
            background: #f1fff1;
        }
        .note-meta {
            font-size: 0.9em;
            color: #888;
            margin-bottom: 6px;
        }
        .xss-warning {
            color: #b71c1c;
            font-size: 0.95em;
            margin-bottom: 10px;
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            padding: 6px 10px;
            border-radius: 4px;
        }
        .note-link {
            display: block;
            background: #f9f9f9;
            border-radius: 8px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.07);
            margin: 12px 0;
            padding: 16px 18px;
            border-left: 5px solid #45a049;
            transition: box-shadow 0.2s, background 0.2s;
            word-break: break-word;
            color: #222;
            text-decoration: none;
            cursor: pointer;
        }
        .note-link:hover {
            box-shadow: 0 2px 12px rgba(69,160,73,0.13);
            background: #f1fff1;
            color: #111;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{'Add a New Note' if lang != 'es' else 'Agregar una Nueva Nota'}}</h1>
        % if message:
            <div style="color: {{'green' if success else 'red'}}; margin-bottom: 10px;">{{message if lang != 'es' else ('Nota agregada exitosamente.' if success else 'El contenido de la nota no puede estar vacío.')}}</div>
        % end
        <form action="/note/add-note" method="POST">
            <textarea name="note" rows="5" required placeholder="{{'Write your note here...' if lang != 'es' else 'Escribe tu nota aquí...'}}"></textarea>
            <br>
            <button type="submit">{{'Add Note' if lang != 'es' else 'Agregar Nota'}}</button>
        </form>
        <h2>{{'Your Notes' if lang != 'es' else 'Tus Notas'}}</h2>
        <div>
            % for i, note in enumerate(notes, 1):
                <a class="note-link" href="/note/{{note['id']}}">
                    {{'Note' if lang != 'es' else 'Nota'}} #{{i}} &mdash; {{'Click to preview' if lang != 'es' else 'Haz clic para ver'}}
                </a>
            % end
        </div>
        <a href="/logout">{{'Logout' if lang != 'es' else 'Cerrar sesión'}}</a>
        <br>
        <a href="/set-lang/en">English</a> | <a href="/set-lang/es">Español</a>
    </div>
</body>
</html>