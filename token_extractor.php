<?php
$url = "https://core-api.kablowebtv.com/api/channels";
$headers = [
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJjZ2QiOiIwOTNkNzIwYS01MDJjLTQxZWQtYTgwZi0yYjgxNjk4NGZiOTUiLCJkaSI6IjBmYTAzNTlkLWExOWItNDFiMi05ZTczLTI5ZWNiNjk2OTY0MCIsImFwdiI6IjEuMC4wIiwiZW52IjoiTElWRSIsImFibiI6IjEwMDAiLCJzcGdkIjoiYTA5MDg3ODQtZDEyOC00NjFmLWI3NmItYTU3ZGViMWI4MGNjIiwiaWNoIjoiMCIsInNnZCI6ImViODc3NDRjLTk4NDItNDUwNy05YjBhLTQ0N2RmYjg2NjJhZCIsImlkbSI6IjAiLCJkY3QiOiIzRUY3NSIsImlhIjoiOjpmZmZmOjEwLjAuMC41IiwiY3NoIjoiVFJLU1QiLCJpcGIiOiIwIn0.bT8PK2SvGy2CdmbcCnwlr8RatdDiBe_08k7YlnuQqJE"
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url . "?checkip=false");
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);

if (!$data || !isset($data['Data']['AllChannels'][0]['StreamData']['HlsStreamUrl'])) {
    die('API yanıtı geçersiz veya kanal bulunamadı');
}

// Token'ı stream URL'sinden çıkar
$streamUrl = $data['Data']['AllChannels'][0]['StreamData']['HlsStreamUrl'];
if (preg_match('/wmsAuthSign=(.*?)(?:$|&)/', $streamUrl, $matches)) {
    $token = $matches[1];
    file_put_contents('token.txt', $token);
    echo "Token güncellendi: " . substr($token, 0, 20) . "...\n";
} else {
    die('Token bulunamadı!');
}

// yeni.m3u dosyasını oku
$m3uFile = 'yeni.m3u';
if (!file_exists($m3uFile)) {
    die("Hata: {$m3uFile} dosyası bulunamadı!");
}

$m3uContent = file_get_contents($m3uFile);

// wmsAuthSign parametresini yeni token ile değiştir
$updatedContent = preg_replace(
    '/wmsAuthSign=[^&\s]+/', 
    'wmsAuthSign=' . $token, 
    $m3uContent
);

// Güncellenmiş içeriği dosyaya yaz
if (file_put_contents($m3uFile, $updatedContent)) {
    echo "M3U dosyası başarıyla güncellendi!\n";
    
    // Kaç tane link güncellendiğini say
    $updateCount = preg_match_all('/wmsAuthSign=/', $updatedContent);
    echo "Toplam {$updateCount} link güncellendi.\n";
} else {
    die("Hata: M3U dosyası güncellenemedi!");
}
?>
