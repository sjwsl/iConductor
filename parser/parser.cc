#include <iostream>

using namespace std;

int main() {
  string s;
  while (getline(cin, s)) {
    if (s.find("midi.Track(") != string::npos) {
      cout << endl;
      continue;
    }
    if (s.find("NoteOnEvent") != string::npos) {
      auto pos = s.find("tick");
      pos = pos + 5;
      while (isdigit(s[pos])) {
        cout << s[pos++];
      }
      cout << " ";
      pos = s.find("data");
      pos = pos + 6;
      while (isdigit(s[pos])) {
        cout << s[pos++];
      }
      cout << " ";
      pos = pos + 2;
      while (isdigit(s[pos])) {
        cout << s[pos++];
      }
      cout << endl;
    }
    if (s.find("NoteOffEvent") != string::npos) {
      auto pos = s.find("tick");
      pos = pos + 5;
      while (isdigit(s[pos])) {
        cout << s[pos++];
      }
      cout << " ";
      pos = s.find("data");
      pos = pos + 6;
      while (isdigit(s[pos])) {
        cout << s[pos++];
      }
      cout << " ";
      cout << 0;
      cout << endl;
    }
  }
}