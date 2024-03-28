// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract SimpleStorage {
    uint public storedData;

    struct People{
        uint num;
        string name;
    }

    People[] people;
    mapping (string => uint) public dictionary;

    function store(uint x) public {
        storedData = x;
    }
    function retrive() public view returns(uint){
        return storedData;
    }

    function addPerson(string memory __name, uint __num) public{
        people.push(People(__num, __name));
        dictionary[__name] = __num;
    }

}