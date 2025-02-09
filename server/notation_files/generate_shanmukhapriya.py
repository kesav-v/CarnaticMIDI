import random

if __name__ == '__main__':
    notes = [
        'M/',
        'P/',
        'd/',
        'n/',
        'S',
        'R',
        'g',
        'M',
        'P',
        'd',
        'n',
        'S*',
        'R*',
        'g*',
        'M*',
        'P*',
    ]
    N = len(notes)
    jumps = list(range(-4, 5))
    current = random.choice(range(N))
    for _ in range(32):
        print(notes[current], end='')
        possible_jumps = [i for i in jumps if 0 <= current + i < N and i != 0]
        current += random.choice(possible_jumps)
