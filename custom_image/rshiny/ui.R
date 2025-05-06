ui <- fluidPage(
	tags$h1("Han Park Users"),
	sidebarPanel(
		dateRangeInput("dates",
			       "Date range",
			       start = as.Date("2023-01-01"),
			       end = Sys.Date()),
		br(),
		br()
	),
	mainPanel(plotOutput("day_han_park"), plotOutput("night_han_park"))
)
