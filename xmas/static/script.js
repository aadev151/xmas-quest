function copy() {
    var field = document.getElementById('url');
    field.select();
    field.setSelectionRange(0, 99999);
    document.execCommand("copy");
    document.getElementById('copied').hidden = false;
    setTimeout(deleteMark, 3000);
}

function deleteMark() {
    document.getElementById('copied').hidden = true;
}

function showWinner() {
    document.getElementById('winnerImage').hidden = false;
    document.getElementById('show').hidden = true;
    document.getElementById('oneMoreGame').hidden = false;
    document.getElementById('congrats').hidden = false;
}