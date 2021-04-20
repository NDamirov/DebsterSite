function checkCookies(){
    let cookieDate = localStorage.getItem('cookieAccepted');
    let cookieDiv = document.getElementById('cookie-div')
    let cookieButton = document.getElementById('cookie-accept');


    if( !cookieDate || (+cookieDate + 31536000000) < Date.now() ){
        cookieDiv.classList.add('show');
    }

    cookieButton.addEventListener('click', function(){
        localStorage.setItem( 'cookieAccepted', Date.now() );
        cookieDiv.classList.remove('show');
    })
}

function showMobile(){
    let sideMenu = document.getElementById('side-menu')
    let menuButton = document.getElementById('mobile-menu-button');

    menuButton.addEventListener('click', function(){  
        showMobileMenu = !showMobileMenu;
        if(showMobileMenu){
            sideMenu.classList.remove('mobile-hide');
            menuButton.innerHTML = "Close";
        }
        else{
            sideMenu.classList.add('mobile-hide');
            menuButton.innerHTML = "Menu";
        }
    })
}

function showDescription(element){
    let label = element.getElementsByClassName("material-icons")[0];
    element = element.closest('div');
    let description = element.getElementsByClassName('description')[0];

    if(description.classList.contains('hidden')){
        description.classList.remove('hidden');
        label.innerHTML = "keyboard_arrow_up"
    }
    else{
        description.classList.add('hidden');
        label.innerHTML = "keyboard_arrow_down"
    }
    
}

var showMobileMenu = false;

checkCookies();
showMobile();