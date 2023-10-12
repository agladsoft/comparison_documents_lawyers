// Остановить процессы перед обновлением страницы
$(window).on('beforeunload', function() {
    $.post('/restart', function(response) {
        console.log(response.message);
    });
});

// Get the modal
var modal = document.getElementById("myModal");
// Get the button that opens the modal
var btn = document.getElementById("show_logs");
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}
// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

const myList = document.getElementById("myList");

// Получаем текст элементов ul
const listItems = myList.getElementsByTagName("li");

//// Функция, которая подсвечивает элемент зеленым цветом
//function highlightItem(itemText) {
//    for (let i = 0; i < listItems.length; i++) {
//        const listItem = listItems[i];
//        if (listItem.textContent === itemText) {
//            listItem.classList.add("highlighted");
//        } else {
//            listItem.classList.remove("highlighted");
//        }
//    }
//}
//
//// Вызываем функцию для выделения элемента
//highlightItem("{{ highlighted_item }}");



function getHighlightItem() {
    setInterval(async function() {
        const response = await fetch("/highlight/", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors'
            });
        const array_text = await response.json();
        const listItems = myList.getElementsByTagName("li");
        for (const element of array_text) {
            for (let i = 0; i < listItems.length; i++) {
                const listItem = listItems[i];
                if (listItem.textContent == element) {
                    listItem.classList.add("highlighted");
                }
            }
        }
    }, 5000);
}

getHighlightItem()



function isObject (n) {
          return Object.prototype.toString.call(n) === '[object Object]';
        }

Dropzone.options.initial = {
    paramName: "file",
    chunking: true,
    forceChunking: true,
    url: "/upload",
    maxFilesize: 1025, // megabytes
    chunkSize: 250000, // bytes,
    dictDefaultMessage: "Поместите сюда исходный файл с расширениями (doc, docx, pdf)",
    success: function(file, response){
        if (isObject(response)) {
            $("textarea#docx").val(response["text"]);
        } else {
            $("textarea#docx").val(response);
        }
        document.getElementsByClassName("dz-filename")[0].getElementsByTagName('span')[0].innerHTML = "Исходный файл"
    },
    error: function(file, response) {
        Swal.fire(
            'Ошибка!',
            'Вы загрузили не поддерживаемый подтип файла или файл поврежден!',
            'error'
        );
    }
}

Dropzone.options.edited = {
    paramName: "file",
    chunking: true,
    forceChunking: true,
    url: "/upload",
    maxFilesize: 1025, // megabytes
    chunkSize: 250000, // bytes
    dictDefaultMessage: "Поместите сюда отредактированный файл с расширениями (doc, docx, pdf)",
    success: function(file, response){
        if (isObject(response)) {
            $("textarea#pdf").val(response["text"]);
        } else {
            $("textarea#pdf").val(response);
        }
        document.getElementsByClassName("dz-filename")[1].getElementsByTagName('span')[0].innerHTML = "Отредактированный файл"
    },
    error: function(file, response) {
        Swal.fire(
            'Ошибка!',
            'Вы загрузили не поддерживаемый подтип файла или файл поврежден!',
            'error'
        );
    }
}

document.getElementById("unified").onclick= async ()=> {
    var threshold = parseInt(document.getElementById('threshold').value);
    var docx = document.getElementById('docx').value;
    var pdf = document.getElementById('pdf').value;
    const dictFile = {"docx": docx, "pdf": pdf, "threshold": threshold};
    document.getElementById("loader").style.display = "block";
    const allButton = document.querySelectorAll('button');
    allButton.forEach(button => {
        button.disabled = true;
    });
    let fetchPromise = await fetch("/unified/", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dictFile),
            mode: 'cors'
        });
    document.getElementById("loader").style.display = "none";
    allButton.forEach(button => {
        button.disabled = false;
    });
    console.log(fetchPromise);
    const response = await fetchPromise.json();
    console.log(response);
    $("textarea#docx").val(response['docx']);
    $("textarea#pdf").val(response['pdf']);
};

document.getElementById("downloadReport").onclick= async ()=> {
    var countError = parseInt(document.getElementById('countError').value);
    var docx = document.getElementById('docx').value
    var pdf = document.getElementById('pdf').value
    var group_paragraph = $("#group_paragraph").is(":checked") ? true : false;
    var fileNameDocx = document.getElementsByClassName("dz-filename")[0].getElementsByTagName('span')[0].innerText
    var fileNamePdf = document.getElementsByClassName("dz-filename")[1].getElementsByTagName('span')[0].innerText
    const dictFile = {
        "docx": docx,
        "pdf": pdf,
        "countError": countError,
        "group_paragraph": group_paragraph,
        "file_name_docx": fileNameDocx,
        "file_name_pdf": fileNamePdf
    }
    console.log(dictFile)
    document.getElementById("loader").style.display = "block";
    const allButton = document.querySelectorAll('button');
    allButton.forEach(button => {
        button.disabled = true;
    });
    let fetchPromise = await fetch("/get_disagreement/", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dictFile),
            mode: 'cors'
        });
    document.getElementById("loader").style.display = "none";
    allButton.forEach(button => {
        button.disabled = false;
    });
    console.log(fetchPromise)
    const blob = await fetchPromise.blob();
    const newBlob = new Blob([blob]);
    const blobUrl = window.URL.createObjectURL(newBlob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.setAttribute('download', `data.docx`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
};