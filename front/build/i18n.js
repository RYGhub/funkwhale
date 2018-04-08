const fs = require('fs');
const path = require('path');
const { gettextToI18next } = require('i18next-conv');

// Convert .po files to i18next files
fs.readdir(path.join(__dirname, '..', '..', 'po'), (err, files) => {
    if (err) {
        return console.log(err)
    }

    for (const file of files) {
        if (file.endsWith('.po')) {
            const lang = file.replace(/\.po$/, '')
            const output = path.join(__dirname, '..', 'static', 'translations', `${lang}.json`)
            fs.readFile(path.join(__dirname, '..', '..', 'po', file), (err, content) => {
                if (err) {
                    return console.log(err)
                }

                gettextToI18next(lang, content).then(res => {
                    fs.writeFile(output, res, err => {
                        if (err) {
                            console.log(err)
                        }
                    })
                })
            })
        }
    }
})

