var express = require('express');
var router = express.Router();
const {spawn} = require("child_process");
var sem = require('semaphore')(5);

router.get('/info', function (req, res, next) {
    res.send("upload to " + process.env.UPLOAD_URL + "(running " + sem.available() + ")");
});

router.get('/', function (req, res, next) {
    sem.take(function () {
        const child = spawn("./archive-upload.sh", [process.env.ARCHIVE_DIR, process.env.UPLOAD_URL]);
        child.stdout.on("data", data => {
            console.log(`stdout: ${data}`);
        });
        child.stderr.on("data", data => {
            console.log(`stderr: ${data}`);
        });
        child.on('error', (error) => {
            console.log(`error: ${error.message}`);
            res.status(500).send(`[ERROR]: ${error.message}`);
        });
        child.on("close", code => {
            console.log(`child process exited with code ${code}`);
            sem.leave()
        });
    })
    res.send();
});

module.exports = router;
