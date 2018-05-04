import Vapor
import Foundation
import TfbCommon

struct EmptyJSON: Content {}

public func routes(_ router: Router) throws {

    router.get("json") { req in
        return Message("Hello, World!")
    }

    router.get("plaintext") { req in
        return "Hello, world!" as StaticString
    }
    
}
