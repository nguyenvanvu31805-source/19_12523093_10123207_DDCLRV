param(
    [string]$SourcePath = "docs/baocao_source.txt",
    [string]$TemplatePath = "",
    [string]$OutputPath = "docs/baocao.docx"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing

$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$source = [System.IO.Path]::GetFullPath((Join-Path $workspace $SourcePath))
if ($TemplatePath) {
    $template = [System.IO.Path]::GetFullPath((Join-Path $workspace $TemplatePath))
} else {
    $templateItem = Get-ChildItem -LiteralPath $workspace -Recurse -Filter "BAO_CAO_MAU.docx" | Select-Object -First 1
    if ($null -eq $templateItem) { throw "Template not found." }
    $template = $templateItem.FullName
}
$output = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputPath))
$buildDir = [System.IO.Path]::GetFullPath((Join-Path $workspace ".docx_build"))

if (-not $buildDir.StartsWith($workspace, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Temporary directory is outside workspace."
}
if (Test-Path -LiteralPath $buildDir) {
    Remove-Item -LiteralPath $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir | Out-Null
[System.IO.Compression.ZipFile]::ExtractToDirectory($template, $buildDir)

function XmlEscape([string]$text) {
    if ($null -eq $text) { return "" }
    return [System.Security.SecurityElement]::Escape($text)
}

function DecodeUtf8([string]$base64) {
    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($base64))
}

function RunXml(
    [string]$text,
    [int]$size = 26,
    [bool]$bold = $false,
    [bool]$italic = $false,
    [string]$color = "000000"
) {
    $b = if ($bold) { "<w:b/>" } else { "" }
    $i = if ($italic) { "<w:i/>" } else { "" }
    $safe = XmlEscape $text
    return "<w:r><w:rPr><w:rFonts w:ascii=`"Times New Roman`" w:hAnsi=`"Times New Roman`" w:eastAsia=`"Times New Roman`"/><w:sz w:val=`"$size`"/><w:szCs w:val=`"$size`"/>$b$i<w:color w:val=`"$color`"/></w:rPr><w:t xml:space=`"preserve`">$safe</w:t></w:r>"
}

function ParaXml(
    [string]$text,
    [string]$kind = "normal"
) {
    switch ($kind) {
        "h1" {
            $r = RunXml $text 32 $true $false
            return "<w:p><w:pPr><w:pStyle w:val=`"Heading1`"/><w:jc w:val=`"center`"/><w:spacing w:before=`"160`" w:after=`"260`"/><w:keepNext/></w:pPr>$r</w:p>"
        }
        "h2" {
            $r = RunXml $text 28 $true $false
            return "<w:p><w:pPr><w:pStyle w:val=`"Heading2`"/><w:spacing w:before=`"180`" w:after=`"100`"/><w:keepNext/></w:pPr>$r</w:p>"
        }
        "h3" {
            $r = RunXml $text 26 $true $true
            return "<w:p><w:pPr><w:pStyle w:val=`"Heading3`"/><w:spacing w:before=`"120`" w:after=`"80`"/><w:keepNext/></w:pPr>$r</w:p>"
        }
        "center" {
            $r = RunXml $text 26 $false $false
            return "<w:p><w:pPr><w:jc w:val=`"center`"/><w:spacing w:after=`"120`" w:line=`"360`" w:lineRule=`"auto`"/></w:pPr>$r</w:p>"
        }
        default {
            $r = RunXml $text 26 $false $false
            return "<w:p><w:pPr><w:jc w:val=`"both`"/><w:ind w:firstLine=`"709`"/><w:spacing w:after=`"80`" w:line=`"360`" w:lineRule=`"auto`"/></w:pPr>$r</w:p>"
        }
    }
}

function PageBreakXml {
    return "<w:p><w:r><w:br w:type=`"page`"/></w:r></w:p>"
}

function TocXml {
    return @"
<w:p>
  <w:pPr><w:spacing w:after="120"/></w:pPr>
  <w:fldSimple w:instr="TOC \o &quot;1-3&quot; \h \z \u">
    <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="26"/></w:rPr><w:t>$(DecodeUtf8 'TeG7pWMgbOG7pWMgdOG7sSDEkeG7mW5nIOKAkyBjaOG7jW4gdG/DoG4gYuG7mSB2w6AgbmjhuqVuIEY5IG7hur91IGPhuqduIGPhuq1wIG5o4bqtdC4=')</w:t></w:r>
  </w:fldSimple>
</w:p>
"@
}

function TableXml([object[]]$rows) {
    if ($rows.Count -eq 0) { return "" }
    $colCount = $rows[0].Count
    $width = [Math]::Floor(9000 / $colCount)
    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.Append("<w:tbl><w:tblPr><w:tblW w:w=`"9000`" w:type=`"dxa`"/><w:jc w:val=`"center`"/><w:tblBorders><w:top w:val=`"single`" w:sz=`"6`" w:color=`"000000`"/><w:left w:val=`"single`" w:sz=`"6`" w:color=`"000000`"/><w:bottom w:val=`"single`" w:sz=`"6`" w:color=`"000000`"/><w:right w:val=`"single`" w:sz=`"6`" w:color=`"000000`"/><w:insideH w:val=`"single`" w:sz=`"4`" w:color=`"808080`"/><w:insideV w:val=`"single`" w:sz=`"4`" w:color=`"808080`"/></w:tblBorders><w:tblCellMar><w:top w:w=`"70`" w:type=`"dxa`"/><w:left w:w=`"80`" w:type=`"dxa`"/><w:bottom w:w=`"70`" w:type=`"dxa`"/><w:right w:w=`"80`" w:type=`"dxa`"/></w:tblCellMar></w:tblPr><w:tblGrid>")
    1..$colCount | ForEach-Object { [void]$sb.Append("<w:gridCol w:w=`"$width`"/>") }
    [void]$sb.Append("</w:tblGrid>")
    for ($r = 0; $r -lt $rows.Count; $r++) {
        [void]$sb.Append("<w:tr>")
        foreach ($cell in $rows[$r]) {
            $shade = if ($r -eq 0) { "<w:shd w:val=`"clear`" w:fill=`"D9EAF7`"/>" } else { "" }
            $run = RunXml ([string]$cell) 22 ($r -eq 0) $false
            [void]$sb.Append("<w:tc><w:tcPr><w:tcW w:w=`"$width`" w:type=`"dxa`"/>$shade<w:vAlign w:val=`"center`"/></w:tcPr><w:p><w:pPr><w:spacing w:after=`"0`" w:line=`"260`" w:lineRule=`"auto`"/></w:pPr>$run</w:p></w:tc>")
        }
        [void]$sb.Append("</w:tr>")
    }
    [void]$sb.Append("</w:tbl><w:p><w:pPr><w:spacing w:after=`"60`"/></w:pPr></w:p>")
    return $sb.ToString()
}

function ImageXml([string]$rid, [string]$path, [string]$caption, [int]$docPrId) {
    $img = [System.Drawing.Image]::FromFile($path)
    try {
        $maxW = 5200000.0
        $maxH = 2900000.0
        $ratio = $img.Width / [double]$img.Height
        $cx = $maxW
        $cy = $cx / $ratio
        if ($cy -gt $maxH) {
            $cy = $maxH
            $cx = $cy * $ratio
        }
        $cx = [int64]$cx
        $cy = [int64]$cy
    } finally {
        $img.Dispose()
    }
    $safeCaption = XmlEscape $caption
    return @"
<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="80" w:after="80"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="$cx" cy="$cy"/><wp:docPr id="$docPrId" name="Figure $docPrId"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="$docPrId" name="Figure $docPrId"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="$rid"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="$cx" cy="$cy"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>
<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="100"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/><w:i/></w:rPr><w:t>$safeCaption</w:t></w:r></w:p>
"@
}

function CoverXml {
    $lines = @(
        @{T=(DecodeUtf8 'QuG7mCBHScOBTyBE4bukQyBWw4AgxJDDgE8gVOG6oE8='); S=28; B=$true; A=80},
        @{T=(DecodeUtf8 'VFLGr+G7nE5HIMSQ4bqgSSBI4buMQyBTxq8gUEjhuqBNIEvhu7ggVEhV4bqsVCBIxq9ORyBZw4pO'); S=28; B=$true; A=720},
        @{T=(DecodeUtf8 'QsOBTyBDw4FPIELDgEkgVOG6rFAgTOG7mk4='); S=36; B=$true; A=180},
        @{T=(DecodeUtf8 'SOG7jEMgTcOBWSBDxqAgQuG6ok4='); S=32; B=$true; A=520},
        @{T=(DecodeUtf8 'WMOCWSBE4buwTkcgSOG7hiBUSOG7kE5HIEThu7AgxJBPw4FO'); S=36; B=$true; A=80},
        @{T=(DecodeUtf8 'Q0jhuqRUIEzGr+G7ok5HIFLGr+G7olUgVkFORw=='); S=36; B=$true; A=520},
        @{T=(DecodeUtf8 'TmfDoG5oOiBLaG9hIGjhu41jIG3DoXkgdMOtbmg='); S=26; B=$false; A=80},
        @{T=(DecodeUtf8 'Q2h1ecOqbiBuZ8Ogbmg6IFRyw60gdHXhu4cgbmjDom4gdOG6oW8gdsOgIEtob2EgaOG7jWMgZOG7ryBsaeG7h3U='); S=26; B=$false; A=360},
        @{T=(DecodeUtf8 'U2luaCB2acOqbjogW8SQaeG7gW4gaOG7jSB0w6puXSDigJMgTVNTVjogMTI1MjMwOTM='); S=26; B=$false; A=80},
        @{T=(DecodeUtf8 'U2luaCB2acOqbjogW8SQaeG7gW4gaOG7jSB0w6puXSDigJMgTVNTVjogMTAxMjMyMDc='); S=26; B=$false; A=80},
        @{T=(DecodeUtf8 'R2nhuqNuZyB2acOqbiBoxrDhu5tuZyBk4bqrbjogW8SQaeG7gW4gaOG7jSB0w6puXQ=='); S=26; B=$false; A=640},
        @{T=(DecodeUtf8 'SMavTkcgWcOKTiDigJMgMjAyNg=='); S=28; B=$true; A=0}
    )
    $sb = [System.Text.StringBuilder]::new()
    foreach ($line in $lines) {
        $run = RunXml $line.T $line.S $line.B $false
        [void]$sb.Append("<w:p><w:pPr><w:jc w:val=`"center`"/><w:spacing w:after=`"$($line.A)`"/></w:pPr>$run</w:p>")
    }
    return $sb.ToString()
}

$figureDir = Join-Path $workspace "docs/figures"
$mediaDir = Join-Path $buildDir "word/media"
$relsPath = Join-Path $buildDir "word/_rels/document.xml.rels"
[xml]$rels = [System.IO.File]::ReadAllText($relsPath, [System.Text.Encoding]::UTF8)
$relNs = "http://schemas.openxmlformats.org/package/2006/relationships"
$imageMap = @{}
$imageNames = @(
    "01_quality_distribution.png",
    "02_alcohol_distribution.png",
    "03_alcohol_vs_quality.png",
    "04_correlation_heatmap.png",
    "05_volatile_acidity_vs_quality.png",
    "model_mae_comparison.png",
    "model_rmse_comparison.png",
    "model_r2_comparison.png"
)
for ($i = 0; $i -lt $imageNames.Count; $i++) {
    $name = $imageNames[$i]
    $src = Join-Path $figureDir $name
    if (-not (Test-Path -LiteralPath $src)) { throw "Missing image: $src" }
    $targetName = "report_$name"
    Copy-Item -LiteralPath $src -Destination (Join-Path $mediaDir $targetName) -Force
    $rid = "rId$([int](101 + $i))"
    $node = $rels.CreateElement("Relationship", $relNs)
    $node.SetAttribute("Id", $rid)
    $node.SetAttribute("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    $node.SetAttribute("Target", "media/$targetName")
    [void]$rels.DocumentElement.AppendChild($node)
    $imageMap[$name] = @{ Rid=$rid; Path=$src }
}
$rels.Save($relsPath)

$content = [System.IO.File]::ReadAllLines($source, [System.Text.Encoding]::UTF8)
$body = [System.Text.StringBuilder]::new()
$paragraph = [System.Collections.Generic.List[string]]::new()
$inTable = $false
$tableRows = [System.Collections.Generic.List[object]]::new()
$docPrId = 100

function FlushParagraph {
    if ($paragraph.Count -gt 0) {
        $text = ($paragraph -join " ").Trim()
        if ($text) { [void]$body.Append((ParaXml $text "normal")) }
        $paragraph.Clear()
    }
}

foreach ($raw in $content) {
    $line = $raw.Trim()
    if ($inTable) {
        if ($line -eq "[/TABLE]") {
            [void]$body.Append((TableXml $tableRows.ToArray()))
            $tableRows.Clear()
            $inTable = $false
        } elseif ($line) {
            $cells = @($line.Split('|') | ForEach-Object { $_.Trim() })
            $tableRows.Add($cells)
        }
        continue
    }
    if ($line -eq "[TABLE]") {
        FlushParagraph
        $inTable = $true
    } elseif ($line -eq "[COVER]") {
        FlushParagraph
        [void]$body.Append((CoverXml))
    } elseif ($line -eq "[PAGEBREAK]") {
        FlushParagraph
        [void]$body.Append((PageBreakXml))
    } elseif ($line -eq "[TOC]") {
        FlushParagraph
        [void]$body.Append((TocXml))
    } elseif ($line -match '^\[IMAGE:([^|]+)\|(.+)\]$') {
        FlushParagraph
        $name = $matches[1].Trim()
        $caption = $matches[2].Trim()
        if (-not $imageMap.ContainsKey($name)) { throw "Undeclared image: $name" }
        $docPrId++
        $info = $imageMap[$name]
        [void]$body.Append((ImageXml $info.Rid $info.Path $caption $docPrId))
    } elseif ($line.StartsWith("### ")) {
        FlushParagraph
        [void]$body.Append((ParaXml $line.Substring(4) "h3"))
    } elseif ($line.StartsWith("## ")) {
        FlushParagraph
        [void]$body.Append((ParaXml $line.Substring(3) "h2"))
    } elseif ($line.StartsWith("# ")) {
        FlushParagraph
        [void]$body.Append((ParaXml $line.Substring(2) "h1"))
    } elseif (-not $line) {
        FlushParagraph
    } else {
        $paragraph.Add($line)
    }
}
FlushParagraph

$sectPr = @"
<w:sectPr>
  <w:headerReference w:type="default" r:id="rId52"/>
  <w:footerReference w:type="default" r:id="rId15"/>
  <w:pgSz w:w="11907" w:h="16840" w:code="9"/>
  <w:pgMar w:top="1417" w:right="1134" w:bottom="1417" w:left="1985" w:header="720" w:footer="720" w:gutter="0"/>
  <w:cols w:space="720"/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>
"@

$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<w:body>
$($body.ToString())
$sectPr
</w:body>
</w:document>
"@
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/document.xml"), $documentXml, [System.Text.UTF8Encoding]::new($false))

$headerXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="right"/><w:pBdr><w:bottom w:val="single" w:sz="4" w:color="808080"/></w:pBdr></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="18"/><w:i/><w:color w:val="666666"/></w:rPr><w:t>$(DecodeUtf8 'ROG7sSDEkW/DoW4gY2jhuqV0IGzGsOG7o25nIHLGsOG7o3UgdmFuZyBi4bqxbmcgaOG7jWMgbcOheQ==')</w:t></w:r></w:p></w:hdr>
"@
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/header5.xml"), $headerXml, [System.Text.UTF8Encoding]::new($false))

$footerXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>
"@
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/footer3.xml"), $footerXml, [System.Text.UTF8Encoding]::new($false))

$settingsPath = Join-Path $buildDir "word/settings.xml"
[xml]$settings = [System.IO.File]::ReadAllText($settingsPath, [System.Text.Encoding]::UTF8)
$wNs = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
$update = $settings.SelectSingleNode("//*[local-name()='updateFields']")
if ($null -eq $update) {
    $update = $settings.CreateElement("w", "updateFields", $wNs)
    $update.SetAttribute("val", $wNs, "true")
    [void]$settings.DocumentElement.AppendChild($update)
} else {
    $update.SetAttribute("val", $wNs, "true")
}
$settings.Save($settingsPath)

$outDir = Split-Path -Parent $output
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
$fileStream = [System.IO.File]::Open($output, [System.IO.FileMode]::CreateNew)
$archive = [System.IO.Compression.ZipArchive]::new($fileStream, [System.IO.Compression.ZipArchiveMode]::Create, $false)
try {
    foreach ($item in Get-ChildItem -LiteralPath $buildDir -Recurse -File) {
        $relative = $item.FullName.Substring($buildDir.Length).TrimStart('\', '/').Replace('\', '/')
        $entry = $archive.CreateEntry($relative, [System.IO.Compression.CompressionLevel]::Optimal)
        $entryStream = $entry.Open()
        $inputStream = [System.IO.File]::OpenRead($item.FullName)
        try { $inputStream.CopyTo($entryStream) }
        finally { $inputStream.Dispose(); $entryStream.Dispose() }
    }
} finally {
    $archive.Dispose()
    $fileStream.Dispose()
}

$pageBreakCount = ([regex]::Matches($documentXml, '<w:br w:type="page"/>')).Count
$chapter1Start = -1
$chapter2Start = -1
$chapter3Start = -1
for ($i = 0; $i -lt $content.Count; $i++) {
    if ($content[$i] -match '^# .+ 1\.') { $chapter1Start = $i }
    elseif ($content[$i] -match '^# .+ 2\.') { $chapter2Start = $i }
    elseif ($content[$i] -match '^# .+ 3\.') { $chapter3Start = $i }
}
$chapter1Pages = (($content[$chapter1Start..($chapter2Start - 1)] | Where-Object { $_ -eq '[PAGEBREAK]' }).Count)
$chapter2Pages = (($content[$chapter2Start..($chapter3Start - 1)] | Where-Object { $_ -eq '[PAGEBREAK]' }).Count)

Write-Output "Created: $output"
Write-Output "Explicit page breaks: $pageBreakCount"
Write-Output "Chapter 1 planned pages: $chapter1Pages"
Write-Output "Chapter 2 planned pages: $chapter2Pages"
if (Test-Path -LiteralPath $buildDir) {
    Remove-Item -LiteralPath $buildDir -Recurse -Force
}
