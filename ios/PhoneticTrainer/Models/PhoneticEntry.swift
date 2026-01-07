import Foundation

struct PhoneticEntry: Identifiable, Hashable {
    let id = UUID()
    let letter: String
    let word: String
}

enum PhoneticAlphabet {
    static let entries: [PhoneticEntry] = [
        PhoneticEntry(letter: "A", word: "Alpha"),
        PhoneticEntry(letter: "B", word: "Bravo"),
        PhoneticEntry(letter: "C", word: "Charlie"),
        PhoneticEntry(letter: "D", word: "Delta"),
        PhoneticEntry(letter: "E", word: "Echo"),
        PhoneticEntry(letter: "F", word: "Foxtrot"),
        PhoneticEntry(letter: "G", word: "Golf"),
        PhoneticEntry(letter: "H", word: "Hotel"),
        PhoneticEntry(letter: "I", word: "India"),
        PhoneticEntry(letter: "J", word: "Juliett"),
        PhoneticEntry(letter: "K", word: "Kilo"),
        PhoneticEntry(letter: "L", word: "Lima"),
        PhoneticEntry(letter: "M", word: "Mike"),
        PhoneticEntry(letter: "N", word: "November"),
        PhoneticEntry(letter: "O", word: "Oscar"),
        PhoneticEntry(letter: "P", word: "Papa"),
        PhoneticEntry(letter: "Q", word: "Quebec"),
        PhoneticEntry(letter: "R", word: "Romeo"),
        PhoneticEntry(letter: "S", word: "Sierra"),
        PhoneticEntry(letter: "T", word: "Tango"),
        PhoneticEntry(letter: "U", word: "Uniform"),
        PhoneticEntry(letter: "V", word: "Victor"),
        PhoneticEntry(letter: "W", word: "Whiskey"),
        PhoneticEntry(letter: "X", word: "X-ray"),
        PhoneticEntry(letter: "Y", word: "Yankee"),
        PhoneticEntry(letter: "Z", word: "Zulu")
    ]
}
