declare function describe(description: string, specDefinitions: () => void): void;
declare function beforeEach(action: () => void | Promise<void>): void;
declare function it(expectation: string, assertion: () => void | Promise<void>): void;
declare function expect<T = unknown>(actual: T): {
  toBeTruthy(): void;
};
