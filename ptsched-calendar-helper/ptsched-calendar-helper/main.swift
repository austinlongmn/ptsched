//
//  main.swift
//  ptsched-calendar-helper
//
//  Created by Austin Long on 8/17/24.
//

import Foundation
import EventKit

if try await EKEventStore().requestFullAccessToEvents() {
	print("Access granted.")
} else {
	print("Access denied.")
}

