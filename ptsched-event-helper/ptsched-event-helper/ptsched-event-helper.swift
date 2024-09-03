//
//  main.swift
//  ptsched-event-helper
//
//  Created by Austin Long on 8/22/24.
//

import Foundation
import EventKit

let verbose = !(CommandLine.arguments.count <= 1) && (CommandLine.arguments[1] == "--verbose" || CommandLine.arguments[1] == "-v")

// MARK: utilities
let calendarTitle = ProcessInfo.processInfo.environment["PTSCHED_DEBUG_CALENDAR"] ?? "Course Work"
let defaultNewEventTitle = "Course Work"

func errorAndExit(_ message: String, exitCode: Int32) -> Never {
	printError(message)
	exit(exitCode)
}

func printError(_ message: String) {
	try! FileHandle.standardError.write(contentsOf: (message + "\n").data(using: .utf8)!)
}

func verboseLog(_ message: String) async {
	if (!verbose) { return }
	await OutputActor.instance.output(message)
}

protocol EventRequest: Identifiable<Int>, Decodable {
	associatedtype Response: EventResponse
	
	func handle() async throws -> Response
}

protocol EventResponse: Identifiable<Int>, Encodable {
	
}

struct DefaultEventResponse: EventResponse {
	var id: Int
}

extension EventRequest {
	func getEventStore() -> EKEventStore {
		EKEventStore()
	}
	
	func getCalendar(eventStore: EKEventStore) async -> EKCalendar {
		guard let calendar = eventStore.calendars(for: .event).filter({ $0.title == calendarTitle }).first else {
			errorAndExit("Invalid calendar", exitCode: 1)
		}
		return calendar
	}
}

struct QueryRequest: EventRequest {
	var id: Int
	var queryStartDate: Date
	var queryEndDate: Date
	
	func handle() async throws -> QueryRequestResponse {
		await verboseLog("Beginning handle")
		let eventStore = getEventStore()
		let calendar = await getCalendar(eventStore: eventStore)
		let startDate = Calendar.current.startOfDay(for: queryStartDate)
		let endDateStartOfDay = Calendar.current.startOfDay(for: queryEndDate)
		let endDate = Calendar.current.date(byAdding: .day, value: 1, to: endDateStartOfDay)!
		
		let predicate = eventStore.predicateForEvents(withStart: startDate, end: endDate, calendars: [calendar])
		let events = eventStore.events(matching: predicate)
		
		var result = [Date: String](minimumCapacity: events.count)
		for event in events {
			result[Calendar.current.startOfDay(for: event.startDate)] = event.eventIdentifier
		}
		
		return QueryRequestResponse(id: id, eventIdentifiers: result)
	}
	
	struct QueryRequestResponse: EventResponse {
		var id: Int
		var eventIdentifiers: [Date: String]
		
		enum CodingKeys: CodingKey {
			case id
			case eventIdentifiers
		}
		
		func encode(to encoder: any Encoder) throws {
			var container: KeyedEncodingContainer<CodingKeys> = encoder.container(keyedBy: CodingKeys.self)
			try container.encode(self.id, forKey: CodingKeys.id)
			try container.encode(prepareDictionaryForJSONEncoding(self.eventIdentifiers), forKey: CodingKeys.eventIdentifiers)
		}
	}
}

struct CreateRequest: EventRequest {
	var id: Int
	var date: Date
	var contents: String
	
	func handle() async throws -> CreateRequestResponse {
		let eventStore = getEventStore()
		let calendar = await getCalendar(eventStore: eventStore)
		
		let newEvent = EKEvent(eventStore: eventStore)
		newEvent.calendar = calendar
		newEvent.startDate = date
		newEvent.endDate = date
		newEvent.title = defaultNewEventTitle
		newEvent.isAllDay = true
		newEvent.notes = contents
		
		try eventStore.save(newEvent, span: .thisEvent)
		
		return CreateRequestResponse(id: id, eventIdentifier: newEvent.eventIdentifier)
	}
	
	struct CreateRequestResponse: EventResponse {
		var id: Int
		var eventIdentifier: String
	}
}

struct UpdateRequest: EventRequest {
	var id: Int
	var eventIdentifier: String
	var contents: String
	
	func handle() async throws -> DefaultEventResponse {
		let eventStore = getEventStore()
		guard let event = eventStore.event(withIdentifier: eventIdentifier) else {
			throw EventHelperError.invalidId
		}
		
		event.notes = contents
		try eventStore.save(event, span: .thisEvent)
		
		return DefaultEventResponse(id: id)
	}
}

struct DeleteRequest: EventRequest {
	var id: Int
	var eventIdentifier: String
	
	func handle() async throws -> DefaultEventResponse {
		let eventStore = getEventStore()
		guard let event = eventStore.event(withIdentifier: eventIdentifier) else {
			throw EventHelperError.invalidId
		}
		
		try eventStore.remove(event, span: .thisEvent)
		
		return DefaultEventResponse(id: id)
	}
}

enum RequestType: String, Hashable {
	case query = "QUERY"
	case create = "CREATE"
	case update = "UPDATE"
	case delete = "DELETE"
	
	var requestType: any EventRequest.Type {
		switch self {
		case .query:
			QueryRequest.self
		case .create:
			CreateRequest.self
		case .update:
			UpdateRequest.self
		case .delete:
			DeleteRequest.self
		}
	}
}

enum EventHelperError: String, LocalizedError {
	case badRequest = "Received bad request"
	case invalidDateFormat = "Invalid date format"
	case invalidCalendar = "Invalid calendar"
	case invalidId = "Invalid ID"

	var errorDescription: String { self.rawValue }
}

let dateFormatter = {
	let result = DateFormatter()
	result.dateFormat = "yyyy-MM-dd"
	return result
}()

func prepareDictionaryForJSONEncoding<T: Encodable>(_ dictionary: Dictionary<Date, T>) -> [String: T] {
	var result = [String: T](minimumCapacity: dictionary.count)
	for (key, value) in dictionary {
		result[dateFormatter.string(from: key)] = value
	}
	return result
}

func parseRequestLine(line: String) throws -> any EventRequest {
	let requestTypeAndDetails = line.split(separator: ":", maxSplits: 1)
	guard requestTypeAndDetails.count == 2 else {
		throw EventHelperError.badRequest
	}
	
	guard let requestType = RequestType(rawValue: String(requestTypeAndDetails[0])) else {
		throw EventHelperError.badRequest
	}
	
	let decoder = JSONDecoder()
	decoder.dateDecodingStrategy = .formatted(dateFormatter)
	
	guard let request = try? decoder.decode(requestType.requestType, from: requestTypeAndDetails[1].data(using: .utf8)!) else {
		throw EventHelperError.badRequest
	}
	
	return request
}

actor OutputActor {
	static var instance = OutputActor()
	
	func respond(response: any EventResponse) async throws {
		await verboseLog("Responding...")
		let encoder = JSONEncoder()
		encoder.dateEncodingStrategy = .formatted(dateFormatter)
		output(String(data: try encoder.encode(response), encoding: .utf8)!)
		await verboseLog("Completed responding.")
	}

	func output(_ message: String) {
		try! FileHandle.standardOutput.write(contentsOf: (message + "\n").data(using: .utf8)!)
	}
	
	private init() {}
}

@main
struct PtschedEventHelper {
	static func main() async {
		do {
			guard try await EKEventStore().requestFullAccessToEvents() else {
				errorAndExit("No access to calendars", exitCode: 13)
			}
			
			try await withThrowingDiscardingTaskGroup { group in
				await verboseLog("Starting server")
				while let line = readLine() {
					await verboseLog("Received request")
					let request = try parseRequestLine(line: line)
					
					group.addTask {
						let response = try await request.handle()
						try await OutputActor.instance.respond(response: response)
					}
					await verboseLog("Added task.")
				}
				await verboseLog("Received all requests.")
			}
		} catch let error as EventHelperError {
			errorAndExit(error.errorDescription, exitCode: 1)
		} catch {
			print("An unexpected error has occurred: \(error)")
		}
	}
}
