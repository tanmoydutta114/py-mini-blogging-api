function longestConsecutive(nums) {
  const numSet = new Set(nums);
  let maxLength = 0;

  for (let num of numSet) {
    if (!numSet.has(num - 1)) {
      let currentNum = num;
      let currentStreak = 1;

      while (numSet.has(currentNum + 1)) {
        currentNum += 1;
        currentStreak += 1;
      }

      maxLength = Math.max(maxLength, currentStreak);
    }
  }

  return maxLength;
}

const input = [100, 4, 200, 1, 3, 2];
console.log(longestConsecutive(input));
