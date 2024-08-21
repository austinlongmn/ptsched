on run argv
	set details to item 1 of argv
	set eventDate to date (item 2 of argv)

	tell application "iCal"
		tell calendar "Course Work"
			set theEvents to events whose start date is equal to eventDate
			if length of theEvents is 0 then
				set theEvent to (make new event at end with properties {description:details, summary:"Course Work", start date:eventDate, end date:eventDate, allday event:true})
			else
				set theEvent to item 1 of theEvents
			end if
			set theEvent's description to details
			return theEvent's uid
		end tell
	end tell
end run
