const ws = new WebSocket('ws://localhost:8000/ws')
let iPlayer = "X"
let otherPlayer
let activeGame = false
let gameState = ["", "", "", "", "", "", "", "", ""]


ws.onopen = function (event){
    console.log(event)
    newUser()
}

ws.onmessage = function (event){
    console.log(event)
    let data = JSON.parse(event.data)
    switch (data.action){
        case 'new' :
            gameList(data.games)
            break
        case 'join' :
            startGame(data.action, data.player, data.other_player, data.game_id)
            break
        case 'create' :
            createdGame(data.player, data.game_id)
            break
        case 'move' :
            moveGame(data.cell, data.move)
            break
        default:
            break
    }
}

function send(data){
    ws.send(JSON.stringify(data))
}

function newUser(){
    send({action: 'new'})
}

function createGame(event){
    send({action: 'create'})
}

function moveGame(cellIndex, move) {

}

function createdGame(state, game_id) {
    iPlayer = state
    newGame(game_id);
}

function joinGame(event){
    let btn = event.target
    send({action: 'join', game: btn.id})
}

function newGame(game_id) {
    document.getElementById('game').className = 'game-off'
    document.getElementById('tic-tac-toe').className = 'game-on'
    let state = document.getElementById('player')
    state.className = 'game-on'
    state.innerHTML = `<p>ID game: <span class="text-underline">${game_id}</span></p><p>You are player: <span class="text-underline">${iPlayer}</span></p>`
}

function showListGames(){
    document.getElementById('game').className = 'game-on'
    document.getElementById('tic-tac-toe').className = 'game-off'
    let state = document.getElementById('player')
    state.className = 'game-off'
    state.innerHTML = ''
}

function startGame(action, player, other_player, game_id){
    iPlayer = player
    otherPlayer = other_player

    newGame(game_id);
}

function gameList(game) {
    showListGames()
    let i = 0
    if (game === 0) {
        // let gameList = document.getElementById('gameList')
        // gameList.removeChild(gameList.lastChild)
        return
    }
    while (i < game){
        let gameList = document.getElementById('gameList')
        let li = document.createElement('li')
        let text = document.createTextNode(`Game ${i}    `)
        let btn = document.createElement('button')
        btn.id = `${i + 1}`
        btn.innerHTML = 'Connect'
        btn.addEventListener('click', joinGame)
        li.appendChild(text)
        li.appendChild(btn)
        gameList.appendChild(li)
        i++
    }
}


function clickCell(event) {
    const cell = event.target
    const cellIndex = parseInt(cell.getAttribute('data-cell-index'))

    if (!activeGame || gameState[cellIndex] !== "") {
        return
    }
    gameState[cellIndex] = iPlayer
    cell.innerHTML = iPlayer

    send({action: 'move', 'cell': cellIndex})
}

function closeGame() {
    send({action: 'close'})
}

document.getElementById('create-game').addEventListener('click', createGame)
document.getElementById('close-game').addEventListener('click', closeGame)


document.querySelectorAll('.cell').forEach(cell => cell.addEventListener('click', clickCell))

