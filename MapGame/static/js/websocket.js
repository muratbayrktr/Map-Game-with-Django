var serveripport = '127.0.0.1:50505'
console.log('websocket.js loaded')
function sendenter(e, f) {
    if (e.keyCode == 13) { f();}
    return false;
}
function addMess() {
    var el = document.getElementById('newmess');
    var inp = el.value;
    var m;
    if ( /^[0-9]+:.*$/.test(inp) ) {
        var t = inp.split(':',2);
        m = { id: t[0], message: t[1]};
    } else {
        m = { id: '*', message: inp};
    }
    ws.socket.send(JSON.stringify(m));
    el.value = "";
}
function addNewId() {
    // add a new message id to listen to
    var newel = document.getElementById("newid");
    var newid = newel.value;
    if (ws.waitids.indexOf(newid) >= 0) // already listening
        return false;

    ws.waitids.push(newid);
    ws.addnewid(newid);
    // restart websocket with new information
    newel.value = "";

    // update DOM with new subscription
    var row=document.createElement("tr");
    row.innerHTML='<td>' + newid + '</td><td><button onClick=\'deleteId("' + newid + '");\'>Remove</button></td></tr>';
    row.setAttribute('id','row' + newid);
    document.getElementById("stable").appendChild(row);
    
}
function deleteId(did) {
    var row = document.getElementById('row' + did);
    var pos = ws.waitids.indexOf(did);

    if (row)
        row.remove();

    if (pos >= 0) {
        ws.waitids.splice(pos,1);
        // restart websocket with new information
        ws.removeid(did);
    }	
}
function newTeam(id) {
    // Check the selected option
    var teamselect = document.getElementById(id);
    var selected = teamselect.options[teamselect.selectedIndex].value;
    if (selected == 'new') {
        // Get the parent node and find the <strong> tag and find mapname
        var mapid = teamselect.parentNode.querySelector('strong').id
        var teamname = document.getElementById(mapid + '_teamname');
        console.log(mapid);
        if (!teamname) {
            teamname = document.createElement('input');
            teamname.setAttribute('type', 'text');
            teamname.setAttribute('id', mapid + '_teamname');
            teamname.setAttribute('placeholder', 'Enter team name');
            teamselect.parentNode.insertBefore(teamname, teamselect.nextSibling);
        }

    } else {
        var mapid = teamselect.parentNode.querySelector('strong').id;
        var teamname = document.getElementById(mapid + '_teamname');
        if (teamname) {
            teamname.remove();
        }
    }
}

function collapse() {
    var x = document.getElementById("maplist");
    x.innerHTML = '';
}




function joinTeam() {
    // Get the parent node and find the <strong> tag and find mapname
    var mapid = event.target.parentNode.querySelector('strong').id;
    var teamselect = document.getElementById(mapid + '_teamselect');
    var teamname = document.getElementById(mapid + '_teamname');
    if (teamname) {
        var team = teamname.value;
    }
    else {
        try {
            var selected = teamselect.options[teamselect.selectedIndex].value;
        } catch(err) {
            console.log('No teams to join');
            return;
        }
        var team = selected;
    }
    // Send join command to the server
    var status = document.getElementById('status');
    status.textContent = 'Sending join';
    status.setAttribute('style','background-color: #ffffa0');
    var username = document.getElementById('username').textContent;
    
    console.log('Sending <join ' + mapid +' ' + username + ' '+ team + '>');
    ws.socket.send(JSON.stringify({command:'join', id: '*',mapid: mapid, username: username, team: team}));

    // Username is sent to the server
}


function listmaps() {
    // Send listmaps command to the server
    var status = document.getElementById('status');
    status.textContent = 'Sending listmaps';
    status.setAttribute('style','background-color: #ffffa0');
    ws.socket.send(JSON.stringify({command:'listmaps', id: 'n/a'}));
}

function newmap() {
    // Send listmaps command to the server
    var status = document.getElementById('status');
    status.textContent = 'Sending newmap';
    status.setAttribute('style','background-color: #ffffa0');
    var mapname = document.getElementById('newmapselect').value;
    const mapwidth = 1024;
    const mapheight = 1024;
    var map = {command:'newmap', id: '*', mapname: mapname, mapwidth: mapwidth, mapheight: mapheight};
    if (mapname == '0') {
        console.log('Invalid map name');
        return;
    }
    ws.socket.send(JSON.stringify(map));
}

function leaveMap() {
    // Send leave command to the server
    var status = document.getElementById('status');
    status.textContent = 'Sending leave';
    status.setAttribute('style','background-color: #ffffa0');
    var id = document.getElementById('player_uuid').textContent;
    var map_uuid = document.getElementById('map_uuid').textContent;
    ws.socket.send(JSON.stringify({command:'leave', id: '*', player_uuid: id, map_uuid: map_uuid}));

    // Clear all the circles and texts except image
    var svg = document.getElementById("map_area"); // SVG
    var circles = svg.getElementsByTagName("circle");
    var texts = svg.getElementsByTagName("text");
    while (circles.length > 0) {
        circles[0].parentNode.removeChild(circles[0]);
    }
    while (texts.length > 0) {
        texts[0].parentNode.removeChild(texts[0]);
    }
    // Clear status
    var status = document.getElementById('status');
    status.textContent = 'Map left.';
    status.setAttribute('style','background-color: #a0ffa0');
    // Clear map
    var map = document.getElementById('map_area');
    map.innerHTML = '<image id="map" alt="Map Placeholder" height="1024" width="1024">';
    // Clear player info
    var player = document.getElementById('game_info');
    player.innerHTML = '';

    // Clear map info
    var map = document.getElementById('map_info');
    map.innerHTML = '';
}



class Ws  {
constructor(wids = []) {
    this.waitids = wids;
    var status = document.getElementById('status');
    // create a web socket
        this.socket = new WebSocket('ws://' + serveripport);
    var socket = this.socket
    socket.onopen = function() {
        // send id list for notifications
        socket.send(JSON.stringify(wids));
        status.textContent = 'Connected';
        status.setAttribute('style','background-color: #a0ffa0');
    }
    socket.onerror = function() {
        status.textContent = 'Connection failed';
        status.setAttribute('style','background-color: #ffa0a0');
    }
    socket.onclose = function() {
        status.textContent = 'Connection closed';
        status.setAttribute('style','background-color: #ffa0a0');
    }

    socket.onmessage = function (event) {
        var messages = JSON.parse(event.data);
        console.log(messages);
        if (!Array.isArray(messages)) {
            messages = [messages];
        }
        for (var mid in messages) {
            if (messages[mid].command == 'listmaps') {
                var maparray = messages[mid].maps;

                var maplist = document.getElementById('maplist');
                maplist.innerHTML = '';
                for (var map in maparray) {
                    var mapitem = document.createElement('li');
                    var teamsArray = maparray[map].teams;
                    if (teamsArray.length == 0) {
                        teamsArray = 'No teams';
                        mapitem.innerHTML = '<strong id = '+ maparray[map].id +'>' + maparray[map].name + '</strong><br>';
                        // There is no team to be joined, create a text field to enter a team name
                        var teamname = document.createElement('input');
                        teamname.setAttribute('type', 'text');
                        teamname.setAttribute('id', maparray[map].id +'_teamname');
                        teamname.setAttribute('placeholder', 'Enter team name');
                        mapitem.appendChild(teamname);
                        // Create a button to join the team
                        var joinbutton = document.createElement('button');
                        joinbutton.setAttribute('onClick', 'joinTeam()');
                        joinbutton.innerHTML = 'Join';
                        mapitem.appendChild(joinbutton);
                        maplist.appendChild(mapitem);
                    } else {
                        // There are teams to be joined, create a dropdown menu to select a team
                        var teamselect = document.createElement('select');
                        teamselect.setAttribute('id', maparray[map].id + '_teamselect');
                        teamselect.setAttribute('onchange', 'newTeam(id)');
                        // On create
                        teamselect.setAttribute('onload', 'newTeam(id)');
                        mapitem.innerHTML = '<strong id = '+ maparray[map].id +'>' + maparray[map].name + '</strong><br>';

                        // Default option is to create a new team, when new is selected input box appears
                        // if other is selected, input box doesn't appear
                        var newOption = document.createElement('option');
                        newOption.setAttribute('value', 'new');
                        newOption.innerHTML = 'New';
                        // When new is selected, input box appears
                        teamselect.appendChild(newOption);
                        for (var team in teamsArray) {
                            var teamoption = document.createElement('option');
                            teamoption.setAttribute('value', teamsArray[team]);
                            teamoption.innerHTML = teamsArray[team];
                            teamselect.appendChild(teamoption);
                        }
                        mapitem.appendChild(teamselect);
                        // Create a button to join the team
                        var joinbutton = document.createElement('button');
                        joinbutton.setAttribute('onClick', 'joinTeam()');
                        joinbutton.innerHTML = 'Join';
                        mapitem.appendChild(joinbutton);
                        maplist.appendChild(mapitem);
                    }
                }
            }
            else if (messages[mid].command == 'setId') {
                // Clear listmaps
                var maplist = document.getElementById('maplist');
                maplist.innerHTML = '';
                // Clear status
                var status = document.getElementById('status');
                status.textContent = 'Map joined.';
                status.setAttribute('style','background-color: #a0ffa0');
                // Clear map
                
                var id = messages[mid].player_id;
                var row=document.createElement("tr");
                row.innerHTML='<td id=player_uuid>' + id + '</td><td><button onClick=leaveMap()>Leave</button></td></tr>';
                row.setAttribute('id','game_info');
                var maprow = document.createElement("tr");
                var mapid = messages[mid].map_id;
                maprow.innerHTML = '<td id=map_uuid>'+ mapid +'</td><td>';
                document.getElementById("stable").appendChild(row);
                document.getElementById("stable").appendChild(maprow);
            }
            else if (messages[mid].command == 'updateMap') {
                console.log('updateMap');
                var map_uuid = document.getElementById('map_uuid').textContent;
                var player_uuid = document.getElementById('player_uuid').textContent;
                var message = {command: 'updateMap', map_uuid: map_uuid, player_uuid: player_uuid};
                socket.send(JSON.stringify(message));
            }
            else if (messages[mid].command == 'loadMap') {
                // base64 format
                var image = messages[mid].image;
                // console.log(image); // Log the base64 string to the console for debugging
            
                // inject image into DOM
                var map = document.getElementById('map');
                if (map) { // Check if the element actually exists
                    map.setAttribute('href', 'data:image/png;base64,' + image);

                    // Clear all the circles and texts except image
                    var svg = document.getElementById("map_area"); // SVG
                    var circles = svg.getElementsByTagName("circle");
                    var texts = svg.getElementsByTagName("text");
                    while (circles.length > 0) {
                        circles[0].parentNode.removeChild(circles[0]);
                    }
                    while (texts.length > 0) {
                        texts[0].parentNode.removeChild(texts[0]);
                    }
                    // Update status
                    var query = messages[mid].query; // array of arrays
                    for (var obj in query) {
                        var objid = query[obj][0];
                        var name = query[obj][1];
                        var type = query[obj][2];
                        var x = query[obj][3];
                        var y = query[obj][4];

                        /* 
                        {% for obj in objects %}
                            <text x="{{ obj.x }}" y="{{ obj.y }}" fill="{{ obj.color }}" font-size="10px">{{ obj.name }}</text>
                            <circle cx="{{ obj.x }}" cy="{{ obj.y }}" r="5" fill="{{ obj.color }}"/>
                        {% endfor %}
                        */

                        var color_mapping = {
                            "Player": "blue",
                            "Mine": "red",
                            "Health": "green",
                            "Freezer": "yellow"
                        }
                        var svg = document.getElementById("map_area"); // SVG 
                        var text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                        text.setAttribute("x", x);
                        text.setAttribute("y", y);
                        text.setAttribute("fill", color_mapping[type]);
                        text.setAttribute("font-size", "10px");
                        text.textContent = name;
                        svg.appendChild(text);
                        var circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                        circle.setAttribute("cx", x);
                        circle.setAttribute("cy", y);
                        circle.setAttribute("r", "5");
                        circle.setAttribute("fill", color_mapping[type]);
                        svg.appendChild(circle);

                    }
                    // Update status
                    var status = document.getElementById('status');
                    if (status) { // Check if the status element exists
                        status.textContent = 'Map loaded.';
                        status.setAttribute('style','background-color: #a0ffa0');
                    } else {
                        console.error('Status element not found');
                    }
                } else {
                    console.error('Map element not found');
                }
            }
        }
    };
}


    addnewid(nid) {
        this.socket.send(JSON.stringify({command:'add',id: nid}))
    }
    removeid(did) {
        this.socket.send(JSON.stringify({command:'delete',id: did}))
    }
}
var ws = new Ws();

document.addEventListener('keydown', function(event) {
    switch(event.keyCode) {
        case 65: // A
            console.log('Left arrow key pressed');
            // move W command
            var map_uuid = document.getElementById('map_uuid').textContent;
            var player_uuid = document.getElementById('player_uuid').textContent;
            var message = {command: 'move', map_uuid: map_uuid, player_uuid: player_uuid, direction: 'W'};
            ws.socket.send(JSON.stringify(message));
            break;
        case 87: // W
            console.log('Up arrow key pressed');
            // move N command
            var map_uuid = document.getElementById('map_uuid').textContent;
            var player_uuid = document.getElementById('player_uuid').textContent;
            var message = {command: 'move', map_uuid: map_uuid, player_uuid: player_uuid, direction: 'N'};
            ws.socket.send(JSON.stringify(message));
            break;
        case 68: // D
            console.log('Right arrow key pressed');
            // move E command
            var map_uuid = document.getElementById('map_uuid').textContent;
            var player_uuid = document.getElementById('player_uuid').textContent;
            var message = {command: 'move', map_uuid: map_uuid, player_uuid: player_uuid, direction: 'E'};
            ws.socket.send(JSON.stringify(message));
            break;
        case 83: // S
            console.log('Down arrow key pressed');
            // move S command
            var map_uuid = document.getElementById('map_uuid').textContent;
            var player_uuid = document.getElementById('player_uuid').textContent;
            var message = {command: 'move', map_uuid: map_uuid, player_uuid: player_uuid, direction: 'S'};
            ws.socket.send(JSON.stringify(message));
            break;
        case 82: // R
            console.log('R key pressed for drop.');
            // move R command
            var map_uuid = document.getElementById('map_uuid').textContent;
            var player_uuid = document.getElementById('player_uuid').textContent;
            var message = {command: 'drop', map_uuid: map_uuid, player_uuid: player_uuid, direction: 'R'};
            ws.socket.send(JSON.stringify(message));
            break;
        default:
            // Handle other keys if needed
            break;
    }
});