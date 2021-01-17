HTML_PAGE_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>%(title)s</title>
</head>
<body>
    %(body)s
</body>
</html>
"""

NOT_FOUND_BODY_TEMPLATE = """
<h1>FILE NOT FOUND</h1>
<div>Go back to <a href="/">Home</a><div/>
"""
NOT_FOUND_PAGE = HTML_PAGE_TEMPLATE % {
    "title": "File not found",
    "body": NOT_FOUND_BODY_TEMPLATE,
}

INTERNAL_SERVER_ERROR_TEMPLATE = """
<h1>INTERNAL SERVER ERROR</h1>
"""
INTERNAL_SERVER_ERROR_PAGE = HTML_PAGE_TEMPLATE % {
    "title": "Server error",
    "body": INTERNAL_SERVER_ERROR_TEMPLATE,
}

DIRECTORY_LISTING_BODY_TEMPLATE = """
<h1>Index of %(relative_requested_path)s</h1>
<hr>
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Last modified</th>
            <th>Size</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        %(listing_html)s
    </tbody>
</table>
<hr>
"""
DIRECTORY_LISTING_TEMPLATE = HTML_PAGE_TEMPLATE % {
    "title": "Index of %(relative_requested_path)s",
    "body": DIRECTORY_LISTING_BODY_TEMPLATE,
}

DIRECTORY_LISTING_ITEM_TEMPLATE = """
<tr>
    <td><a href="%(html_path)s">%(name)s</a></td>
    <td>%(last_modified)s</td>
    <td>%(size)s</td>
    <td>%(actions)s</td>
</tr>
"""
