//
//  main.swift
//  ptsched-event-helper
//
//  Created by Austin Long on 8/22/24.
//

import Foundation
import EventKit

// MARK: utilities
func printToSTDERR(_ message: String) {
	try! FileHandle.standardError.write(contentsOf: (message + "\n").data(using: .utf8)!)
}

let calendarTitle = ProcessInfo.processInfo.environment["PTSCHED_DEBUG_CALENDAR"] ?? "Course Work"
let defaultNewEventTitle = "Course Work"

// MARK: main function
@Sendable
func handleRequest(request: Request) async throws {
	let startOfDay = Calendar.current.startOfDay(for: request.date)
	let endOfDay = Calendar.current.date(byAdding: .day, value: 1, to: startOfDay)!
	
	let eventStore = EKEventStore()
	
	guard try await eventStore.requestFullAccessToEvents() else {
		printToSTDERR("Error: no access to calendar events.")
		exit(13)
	}
	
	guard let calendar = eventStore.calendars(for: .event).filter({ $0.title == calendarTitle }).first else {
		printToSTDERR("Invalid calendar.")
		exit(1)
	}
	
	switch request.requestTypeAndValue {
	case .update(let contents):
		let predicate = eventStore.predicateForEvents(withStart: startOfDay, end: endOfDay, calendars: [calendar])
		var events = eventStore.events(matching: predicate)
		
		if events.isEmpty {
			let newEvent = EKEvent(eventStore: eventStore)
			newEvent.calendar = calendar
			newEvent.startDate = request.date
			newEvent.endDate = request.date
			newEvent.title = defaultNewEventTitle
			newEvent.isAllDay = true
			events.append(newEvent)
		}
		
		for event in events {
			event.notes = contents
			try eventStore.save(event, span: .thisEvent)
		}
	case .delete:
		break
	}

	print(request.id)
}

enum ReadingStatus {
	case id
	case requestType(Int)
	case date(Int, RequestType)
	case contents(Int, RequestType, Date, String)
}

struct Request: Identifiable, Hashable {
	var id: Int
	var date: Date
	var requestTypeAndValue: RequestTypeAndValue
}

enum RequestTypeAndValue: Hashable {
	case update(contents: String)
	case delete
}

enum RequestType: String, Hashable {
	case update = "UPDATE"
	case delete = "DELETE"
}

enum EventHelperError: String, LocalizedError {
	case badRequest = "Received bad request"
	case invalidDateFormat = "Invalid date format"
	case invalidCalendar = "Invalid calendar"

	var errorDescription: String? { self.rawValue }
}

let dateFormatter = DateFormatter()
dateFormatter.dateFormat = "yyyy-MM-dd"

func parseRequestLine(line: String, status: inout ReadingStatus) throws -> Request? {
	switch status {
	case .id:
		guard let id = Int(line) else {
			printToSTDERR("id error")
			throw EventHelperError.badRequest
		}
		
		status = .requestType(id)
	case .requestType(let id):
		guard let requestType = RequestType(rawValue: line) else {
			printToSTDERR("requestType error")
			throw EventHelperError.badRequest
		}
		status = .date(id, requestType)
	case .date(let id, let requestType):
		guard let date = dateFormatter.date(from: line) else {
			printToSTDERR("date format error")
			throw EventHelperError.invalidDateFormat
		}
		
		if requestType == .delete {
			status = .id
			return Request(id: id, date: date, requestTypeAndValue: .delete)
		} else {
			status = .contents(id, requestType, date, "")
		}
	case .contents(let id, let requestType, let date, let contents):
		if line == "END REQUEST" {
			status = .id
			return Request(id: id, date: date, requestTypeAndValue: .update(contents: contents))
		} else {
			status = .contents(id, requestType, date, contents + line + "\n")
		}
	}
	
	return nil
}

do {
	try await withThrowingDiscardingTaskGroup { group in
		var status = ReadingStatus.id
		while let line = readLine() {
			if let request = try parseRequestLine(line: line, status: &status) {
				group.addTask {
					try await handleRequest(request: request)
				}
			}
		}
	}
} catch let error as EventHelperError {
	printToSTDERR(error.rawValue)
	exit(1)
}
