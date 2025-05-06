server <- function(input, output){
	selected_data <- reactive({
        	# Connect to the DB
        	conn <- dbConnect(
                  RPostgres::Postgres(),
                  dbname = "postgres",
                  host = "172.28.0.3",
                  port = "5432",
                  user = "postgres",
                  password = "postgres"
		)
        	# Get the data
        	park <- dbGetQuery(conn, glue("SELECT 
						 to_date(substring(\"STATS_DT\",1,10),'YYYY.MM.DD') as s_dt
					       	,\"CNT2\"::float as day_users
						,\"CNT3\"::float  as night_users
						FROM \"han_park_info_v2\" 
						WHERE \"PARK_CD\" ='Hzone007' and to_date(substring(\"REG_DT\",1,10),'YYYY.MM.DD') BETWEEN '{format(input$dates[1])}' AND '{format(input$dates[2])}'"))
        	# Disconnect from the DB
        	dbDisconnect(conn)
        	# Convert to data.frame
        	data.frame(park)
	})
	
	output$day_han_park <- renderPlot({
		ggplot(data=selected_data(), aes(x=s_dt, y=day_users)) + 
			geom_line(color='blue', linewidth = 1) + 
			geom_point(color='red') + 
			geom_smooth(method='lm') +
			ggtitle("Daily Park Users in day time") +
			labs(x='Date',y='Day Users')
	})
	output$night_han_park <- renderPlot({
               ggplot(data=selected_data(), aes(x=s_dt, y=night_users)) +
               geom_line(color='blue', linewidth = 1) +
               geom_point(color='red') +
               geom_smooth(method='lm') +
	       ggtitle("Daily Park Users at night") +
               labs(x='Date',y='Night Users')
        })

}
