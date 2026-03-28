$root = "C:\Users\david\Projects\RODZAKI.github.io"
$files = Get-ChildItem -Path $root -Recurse -Filter "*.html"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName)
    $content = $content.Replace("G??", "&rarr;")
    if (-not ($content -match "charset")) {
        $content = $content.Replace("<head>", "<head>`n<meta charset=""UTF-8"">")
    }
    [System.IO.File]::WriteAllText($file.FullName, $content, $utf8NoBom)
    Write-Host "Processed: $($file.FullName)"
}