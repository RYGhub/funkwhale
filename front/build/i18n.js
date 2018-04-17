const fs = require('fs');
const path = require('path');
const { gettextToI18next } = require('i18next-conv');

const poDir = path.join(__dirname, '..', '..', 'po')
const outDir = path.join(__dirname, '..', 'static', 'translations')
if (!fs.existsSync(outDir) || !fs.statSync(outDir).isDirectory()) {
    fs.mkdirSync(outDir)
}

// Convert .po files to i18next files
fs.readdir(poDir, (err, files) => {
    if (err) {
        return console.log(err)
    }

    for (const file of files) {
        if (file.endsWith('.po')) {
            const lang = file.replace(/\.po$/, '')
            const output = path.join(outDir, `${lang}.json`)
            fs.readFile(path.join(poDir, file), (err, content) => {
                if (err) {
                    return console.log(err)
                }

                gettextToI18next(lang, content).then(res => {
                    fs.writeFile(output, res, err => {
                        if (err) {
                            console.log(err)
                        } else {
                            console.log(`Wrote translation file: ${output}`)
                            if (lang === 'en') {
                                // for english, we need to specify that json values are equal to the keys.
                                // otherwise we end up with empty strings on the front end for english
                                var contents = fs.readFileSync(output)
                                var jsonContent = JSON.parse(contents)
                                var finalContent = {}
                                Object.keys(jsonContent).forEach(function(key) {
                                    finalContent[key] = key
                                })
                                fs.writeFile(output, JSON.stringify(finalContent))
                            }
                        }
                    })
                })
            })
        }
    }
})
