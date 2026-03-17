const express = require("express")
const http = require("http")
const {Server} = require("socket.io")
const cors = require("cors")

const app = express()
app.use(cors())
const server = http.createServer(app)
const io = new Server(server, {
    cors: {
        origin: "*",
    }
})

io.on("connection", (socket)=>{
    console.log("user connected:", socket.id);
    socket.on('disconnect', ()=>{
        console.log("user disconnected", socket.id)
    })
})

app.post("/notify", express.json(), (req,res)=>{
    const poRn = req.body.poRn
    io.emit("po_created", {
        poRn: poRn
    })
    res.json({ message: poRn})
})

server.listen(3000,()=>{
    console.log("Socket server running on port 3000")
})