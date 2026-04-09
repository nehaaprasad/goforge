package greet

import "testing"

func TestHello(t *testing.T) {
	if Hello() != "hello" {
		t.Fatalf("Hello() = %q, want %q", Hello(), "hello")
	}
}
