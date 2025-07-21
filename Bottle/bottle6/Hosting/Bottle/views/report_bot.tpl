<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <title>Report Note to Bot</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>Report Note to Admin Bot</h1>
        % if message:
            <div style="color: {{'green' if success else 'red'}}; margin-bottom: 10px;">{{message}}</div>
        % end
        <form method="post" action="/bot">
            <label for="note_id">Note ID:</label>
            <input type="text" id="note_id" name="note_id" required>
            <button type="submit">Report</button>
        </form>
        <a href="/">Back to Home</a>
    </div>
</body>
</html>
