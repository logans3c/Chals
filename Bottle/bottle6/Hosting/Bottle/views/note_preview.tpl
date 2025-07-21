<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{'Note Preview' if lang != 'es' else 'Vista de Nota'}}</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .note-preview {
            background: #f9f9f9;
            border-radius: 8px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.07);
            margin: 24px 0;
            padding: 24px 22px;
            border-left: 5px solid #45a049;
            word-break: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{'Note Preview' if lang != 'es' else 'Vista de Nota'}}</h1>
        <div class="note-preview">
            {{!note['content']}}
        </div>
        <a href="/note/add-note">&larr; {{'Back to Notes' if lang != 'es' else 'Volver a Notas'}}</a>
        <br>
        <a href="/set-lang/en">English</a> | <a href="/set-lang/es">Español</a>
    </div>
</body>
</html>
