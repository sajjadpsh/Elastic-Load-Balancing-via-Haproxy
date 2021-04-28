<?php
$run = false;

exec("sudo stress-ng --cpu 0 -l 85 --vm 1 --vm-bytes 85% --timeout 60s".' > /dev/null 2>/dev/null &');
$run = true;

if ($run) {
  echo 'Executed on background for 60 seconds.<br><br>';
}
?>

