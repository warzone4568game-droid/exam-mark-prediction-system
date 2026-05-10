Set-Location 'C:\Users\Ruban\Desktop\projects\finial_pro'
& 'C:\Program Files\Git\bin\git' add .
$tree = & 'C:\Program Files\Git\bin\git' write-tree
$msg = 'Initial commit: Exam Mark Prediction System'
$new = $msg | & 'C:\Program Files\Git\bin\git' commit-tree $tree
& 'C:\Program Files\Git\bin\git' update-ref refs/heads/main $new
& 'C:\Program Files\Git\bin\git' log --oneline --decorate --graph -n 5
