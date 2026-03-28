$root = "C:\Users\david\Projects\RODZAKI.github.io"
$files = Get-ChildItem -Path $root -Recurse -Filter "*.html"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

foreach ($file in $files) {
    $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
    $content = [System.Text.Encoding]::UTF8.GetString($bytes)
    $content = $content.Replace("G`u{25C6}`u{25C6}", "&rarr;")
    $content = $content.Replace("G" + [char]0xFFFD + [char]0xFFFD, "&rarr;")
    if (-not ($content -match "charset")) {
        $content = $content.Replace("<head>", "<head>`n<meta charset=""UTF-8"">")
    }
    [System.IO.File]::WriteAllText($file.FullName, $content, $utf8NoBom)
    Write-Host "Processed: $($file.FullName)"
}