function dashboardViewToggle() {
	var line = document.getElementById("lineView");
	var grid = document.getElementById("gridView");
	if (line.style.display === "none" && grid.style.display === "inline") {
		line.style.display = "block";
		grid.style.display = "none";
	} else {
		line.style.display = "none";
		grid.style.display = "inline";
	}
}
