<?php
header("Content-Type: audio/x-mpegurl");

$json_url = "https://raw.githubusercontent.com/by-kerimoff/YouTube-Live-JSON/main/output/live.json";
$data = json_decode(file_get_contents($json_url), true);

echo "#EXTM3U\n";

foreach ($data as $ch) {
    $name = $ch['name'];
    $url = $ch['m3u8'];
    echo "#EXTINF:-1,{$name}\n";
    echo $url . "\n";
}
