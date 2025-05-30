function majorityElement(nums) {
  let count = 0;
  let candidate = null;

  for (let num of nums) {
    if (count === 0) {
      candidate = num;
    }
    count += num === candidate ? 1 : -1;
  }

  return candidate;
}

const input = [2, 2, 1, 1, 1, 2, 2];
console.log(majorityElement(input));
