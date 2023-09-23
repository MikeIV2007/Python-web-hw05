console.log('Running...')

const ws = new WebSocket('ws://localhost:8080') //connectes to the local host port 8080

// sends message to server form fild next to the button send
formChat.addEventListener('submit', (e) => {
  e.preventDefault()
  ws.send(textField.value)
  textField.value = null
})

//  hand shaiking
ws.onopen = (e) => {
  console.log('Hello WebSocket!')
}

// sends messages form server
ws.onmessage = (e) => {
  console.log(e.data)
  text = e.data

  const elMsg = document.createElement('div')
  elMsg.textContent = text
  subscribe.appendChild(elMsg)
}